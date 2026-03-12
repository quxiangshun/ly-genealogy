import { getDb } from '../db/connection.js';
import { rebuildPaths } from './path-rebuild.js';

const ANCESTOR_M = [
  '自己',
  '父亲',
  '祖父',
  '曾祖父',
  '高祖父',
  '天祖父',
  '烈祖父',
  '太祖父',
  '远祖父',
  '鼻祖',
];
const ANCESTOR_F = [
  '自己',
  '母亲',
  '祖母',
  '曾祖母',
  '高祖母',
  '天祖母',
  '烈祖母',
  '太祖母',
  '远祖母',
  '鼻祖母',
];
const DESC_M = [
  '自己',
  '儿子',
  '孙子',
  '曾孙',
  '玄孙',
  '来孙',
  '晜孙',
  '仍孙',
  '云孙',
  '耳孙',
];
const DESC_F = [
  '自己',
  '女儿',
  '孙女',
  '曾孙女',
  '玄孙女',
  '来孙女',
  '晜孙女',
  '仍孙女',
  '云孙女',
  '耳孙女',
];
const SIBLING_RANK: Record<number, string> = {
  1: '亲',
  2: '堂',
  3: '族',
};

function genLabel(
  labels: readonly string[],
  n: number,
  isAncestor: boolean
): string {
  if (n < labels.length) return labels[n];
  return `${n}世` + (isAncestor ? '祖' : '孙');
}

export interface LcaMember {
  id: number;
  name: string;
  genealogy_id: number;
}

export interface RelationshipResult {
  relation: string;
  lca: LcaMember;
  upA: number;
  upB: number;
  chainA: LcaMember[];
  chainB: LcaMember[];
}

function getAncestorIds(path: string | null): number[] {
  if (!path || !path.trim()) return [];
  return path
    .trim()
    .split('/')
    .filter((x) => x)
    .map((x) => parseInt(x, 10))
    .filter((n) => !isNaN(n));
}

export function findRelationship(
  memberAId: number,
  memberBId: number
): RelationshipResult | null {
  const db = getDb();

  if (memberAId === memberBId) {
    const row = db
      .prepare('SELECT id, name, genealogy_id FROM family_member WHERE id = ?')
      .get(memberAId) as { id: number; name: string; genealogy_id: number } | undefined;
    if (!row) return null;
    return {
      relation: '同一人',
      lca: row,
      upA: 0,
      upB: 0,
      chainA: [],
      chainB: [],
    };
  }

  const memberA = db
    .prepare(
      'SELECT id, name, genealogy_id, path, gender FROM family_member WHERE id = ?'
    )
    .get(memberAId) as
    | { id: number; name: string; genealogy_id: number; path: string | null; gender: string }
    | undefined;
  const memberB = db
    .prepare(
      'SELECT id, name, genealogy_id, path, gender FROM family_member WHERE id = ?'
    )
    .get(memberBId) as
    | { id: number; name: string; genealogy_id: number; path: string | null; gender: string }
    | undefined;

  if (!memberA || !memberB) return null;
  if (memberA.genealogy_id !== memberB.genealogy_id) return null;

  if (!memberA.path || !memberB.path) {
    rebuildPaths(memberA.genealogy_id);
    const refreshedA = db
      .prepare('SELECT path FROM family_member WHERE id = ?')
      .get(memberAId) as { path: string | null };
    const refreshedB = db
      .prepare('SELECT path FROM family_member WHERE id = ?')
      .get(memberBId) as { path: string | null };
    memberA.path = refreshedA.path;
    memberB.path = refreshedB.path;
  }

  const idsA = getAncestorIds(memberA.path);
  const idsB = getAncestorIds(memberB.path);

  if (idsA.length === 0) idsA.push(memberA.id);
  if (idsB.length === 0) idsB.push(memberB.id);

  let lcaIdx = -1;
  for (let i = 0; i < Math.min(idsA.length, idsB.length); i++) {
    if (idsA[i] === idsB[i]) {
      lcaIdx = i;
    } else {
      break;
    }
  }

  if (lcaIdx === -1) return null;

  const lcaId = idsA[lcaIdx];
  const upA = idsA.length - 1 - lcaIdx;
  const upB = idsB.length - 1 - lcaIdx;

  const lcaRow = db
    .prepare('SELECT id, name, genealogy_id FROM family_member WHERE id = ?')
    .get(lcaId) as { id: number; name: string; genealogy_id: number } | undefined;
  if (!lcaRow) return null;

  const lca: LcaMember = lcaRow;

  const chainAIds = idsA.slice(lcaIdx);
  const chainBIds = idsB.slice(lcaIdx + 1);

  const getMember = (id: number): LcaMember | null => {
    const r = db
      .prepare('SELECT id, name, genealogy_id FROM family_member WHERE id = ?')
      .get(id) as { id: number; name: string; genealogy_id: number } | undefined;
    return r ?? null;
  };

  const chainA: LcaMember[] = chainAIds
    .map((id) => getMember(id))
    .filter((m): m is LcaMember => m !== null);
  const chainB: LcaMember[] = chainBIds
    .map((id) => getMember(id))
    .filter((m): m is LcaMember => m !== null);

  const genderB = memberB.gender || 'M';

  let relation: string;
  if (upB === 0) {
    const labels = genderB === 'M' ? ANCESTOR_M : ANCESTOR_F;
    relation = `${memberB.name} 是 ${memberA.name} 的 ${genLabel(labels, upA, true)}`;
  } else if (upA === 0) {
    const labels = genderB === 'M' ? DESC_M : DESC_F;
    relation = `${memberB.name} 是 ${memberA.name} 的 ${genLabel(labels, upB, false)}`;
  } else if (upA === upB) {
    const rank = SIBLING_RANK[upA] ?? '远房';
    const sib = genderB === 'M' ? '兄弟' : '姐妹';
    relation = `${memberA.name} 与 ${memberB.name} 是${rank}${sib}（共同祖先：${lca.name}）`;
  } else {
    const genDiff = Math.abs(upA - upB);
    if (upA > upB) {
      relation = `${memberB.name} 比 ${memberA.name} 高 ${genDiff} 辈（共同祖先：${lca.name}）`;
    } else {
      relation = `${memberA.name} 比 ${memberB.name} 高 ${genDiff} 辈（共同祖先：${lca.name}）`;
    }
  }

  return {
    relation,
    lca,
    upA,
    upB,
    chainA,
    chainB,
  };
}
