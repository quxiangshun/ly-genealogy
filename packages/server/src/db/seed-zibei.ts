/**
 * Seed generation/zibei data for genealogies that are missing it.
 * Run: npx tsx packages/server/src/db/seed-zibei.ts
 */
import { getDb } from './connection.js';
import { initSchema } from './schema.js';

interface ZibeiData {
  genealogy_name_like: string;
  characters: string;
  note?: string;
}

const ZIBEI: ZibeiData[] = [
  {
    genealogy_name_like: '%贵州余庆%',
    characters: '正开文启世单如仕大光明永远昌万代兴隆凡宗祖',
    note: '自正四郎起，凡字辈为第25世',
  },
  {
    genealogy_name_like: '%湘鄉%四修%',
    characters: '添志思彦伯仲叔季永兴隆盛昌明显达继述荣光',
    note: '湘乡长塘屈氏',
  },
  {
    genealogy_name_like: '%雙峰%五修%',
    characters: '添志思彦伯仲叔季永兴隆盛昌明显达继述荣光扬清世绪贻泽延长',
    note: '湘乡长塘屈氏，与四修谱同源',
  },
  {
    genealogy_name_like: '%陕西渭南%',
    characters: '仲效元景怀德永昌文运鸿开世代荣光忠孝传家远诗书继世长',
    note: '陕西渭南屈氏字辈排行',
  },
  {
    genealogy_name_like: '%东北%源流%',
    characters: '广德明仁义礼智信忠孝传家远诗书继世长',
    note: '辽宁本溪屈氏',
  },
  {
    genealogy_name_like: '%衡阳%',
    characters: '学成先进修德方能立功名扬天下志光宗耀祖庭',
    note: '湖南衡阳屈氏',
  },
  {
    genealogy_name_like: '%溆浦%',
    characters: '国正天心顺官清民自安世代忠良远诗书启后昆',
    note: '湖南溆浦屈氏',
  },
  {
    genealogy_name_like: '%秭归%',
    characters: '大道之行天下为公选贤与能讲信修睦',
    note: '湖北秭归屈氏',
  },
  {
    genealogy_name_like: '%临海%世谱',
    characters: '永嘉肇基崇德广业敬守先训克昌厥后',
    note: '江苏常熟临海屈氏',
  },
  {
    genealogy_name_like: '%常熟%十九卷%',
    characters: '永嘉肇基崇德广业敬守先训克昌厥后',
    note: '常熟临海屈氏，与世谱同源',
  },
];

function seedZibei(): void {
  const db = getDb();
  initSchema(db);

  const findGenealogy = db.prepare('SELECT id, genealogy_name FROM genealogy_main WHERE genealogy_name LIKE ?');
  const countGens = db.prepare('SELECT COUNT(*) AS cnt FROM genealogy_generation WHERE genealogy_id = ?');
  const insertGen = db.prepare(
    'INSERT INTO genealogy_generation (genealogy_id, sort_order, character, note) VALUES (?, ?, ?, ?)'
  );

  let totalAdded = 0;

  for (const item of ZIBEI) {
    const row = findGenealogy.get(item.genealogy_name_like) as { id: number; genealogy_name: string } | undefined;
    if (!row) {
      console.log(`  [跳过] 未找到族谱：${item.genealogy_name_like}`);
      continue;
    }

    const { cnt } = countGens.get(row.id) as { cnt: number };
    if (cnt > 0) {
      console.log(`  [跳过] 已有 ${cnt} 条字辈：${row.genealogy_name}`);
      continue;
    }

    const chars = item.characters.split('');
    const insertMany = db.transaction(() => {
      for (let i = 0; i < chars.length; i++) {
        insertGen.run(row.id, i, chars[i], i === 0 ? item.note : null);
      }
    });
    insertMany();

    totalAdded += chars.length;
    console.log(`  [新增] ${row.genealogy_name}：${chars.length} 字 (${item.characters})`);
  }

  console.log(`\n完成：共新增 ${totalAdded} 条字辈记录。`);
}

seedZibei();
process.exit(0);
