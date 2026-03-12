#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 —— 推倒重建，一次导入全部数据。
运行：python -m scripts.init_data
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, GenealogyMain, GenealogyGeneration, FamilyMember

# ============================================================
# 全部族谱（合并 seed / import_zupu / enrich 三脚本数据）
# ============================================================
ALL_GENEALOGIES = [
    {
        "surname": "屈",
        "genealogy_name": "江苏常熟临海屈氏世谱十九卷",
        "region": "江苏常熟",
        "period": "清道光十年、光绪九年刊本",
        "volumes": "十九卷",
        "hall_name": "三闾祠堂（道光本）、忠义堂（光绪本）",
        "source_url": None,
        "founder_info": "始迁祖屈裳黻字崇益（宋），南城支祖屈颛字诚轩（明）。清屈厚基、屈廷衔修（道光十年），后屈轶续修（光绪九年）。",
        "collection_info": "藏河北大学图书馆、中山大学图书馆、中国国家图书馆、苏州大学图书馆（仅存第12～19卷）。",
        "scattered_region": "江苏省常熟县",
        "description": "藏于河北大学图书馆、中山大学图书馆、中国国家图书馆等。",
    },
    {
        "surname": "屈",
        "genealogy_name": "临海屈氏世谱",
        "region": "江苏常熟",
        "period": "民国11年(1922)",
        "volumes": "6册",
        "hall_name": None,
        "source_url": "https://www.zupu.cn/zhpk/215148",
        "founder_info": "常熟始迁祖屈裳黻字崇益（宋），南城支祖屈颛字诚轩（明）。",
        "collection_info": "zupu.cn 华夏谱库收录，可在线查阅。",
        "scattered_region": "江苏省常熟县",
        "description": "原书民国11年(1922)刊，6册，世系表、插图。版心题：屈氏世谱。",
        "founders": [
            {"name": "屈裳黻", "gender": "M", "courtesy_name": "字崇益", "notes": "常熟始迁祖，宋。"},
            {"name": "屈颛", "gender": "M", "courtesy_name": "字诚轩", "notes": "南城支祖，明。"},
        ],
    },
    {
        "surname": "屈",
        "genealogy_name": "湖北秭归屈氏族谱一卷",
        "region": "湖北秭归",
        "period": "民国12年(1923)",
        "volumes": "一卷",
        "hall_name": None,
        "source_url": None,
        "founder_info": "屈家升、屈家民纂。秭归为屈原故里。",
        "collection_info": "藏湖北省秭归县屈原纪念馆。",
        "scattered_region": "湖北省秭归县",
        "description": "屈家升、屈家民纂。湖北秭归为屈原故里。",
    },
    {
        "surname": "屈",
        "genealogy_name": "湖南溆浦县屈氏族谱一卷",
        "region": "湖南溆浦县",
        "period": "木刻活字印本",
        "volumes": "一卷",
        "hall_name": None,
        "source_url": None,
        "founder_info": "溆浦屈氏与楚地屈氏迁徙相关。",
        "collection_info": "有明确收藏记录（具体馆藏待考）。",
        "scattered_region": "湖南省溆浦县",
        "description": "湖南溆浦屈氏与楚地屈氏迁徙、郡望堂号研究相关。",
    },
    {
        "surname": "屈",
        "genealogy_name": "衡阳屈氏宗谱",
        "region": "湖南衡阳",
        "period": "木刻活字印本",
        "volumes": None,
        "hall_name": None,
        "source_url": None,
        "founder_info": "著者待考。屈楚平自称屈原第七十代孙。",
        "collection_info": "藏四川省双流县屈楚平处。",
        "scattered_region": "湖南省衡阳市",
        "description": "著者待考。藏于四川省双流县自称屈原第七十代孙屈楚平处。",
    },
    {
        "surname": "屈",
        "genealogy_name": "东北屈氏源流史谱",
        "region": "辽宁本溪",
        "period": "2008年5月稿本",
        "volumes": None,
        "hall_name": None,
        "source_url": None,
        "founder_info": "屈广兴编著（2008年5月稿本）。",
        "collection_info": "藏辽宁省本溪市东明区屈广兴处。",
        "scattered_region": "辽宁省本溪市",
        "description": "屈广兴编著。藏于辽宁省本溪市东明区屈广兴处。",
    },
    {
        "surname": "屈",
        "genealogy_name": "陕西渭南屈氏族谱（屈仲辉提供）",
        "region": "陕西渭南",
        "period": "现代整理",
        "volumes": None,
        "hall_name": None,
        "source_url": None,
        "founder_info": "资料由陕西渭南屈仲辉提供，含屈氏八大起源、郡望堂号、历代名人、各地字辈排行等，已作为本站屈氏文化主要参考。",
        "collection_info": "民间整理，屈仲辉提供。",
        "scattered_region": "陕西省渭南市",
        "description": "资料由陕西渭南屈仲辉提供，含屈氏起源、迁徙分布、字辈排行、郡望堂号、名人等。",
        "founders": [
            {
                "name": "屈瑕", "gender": "M",
                "courtesy_name": "即莫敖瑕",
                "notes": "楚武王之子，官至莫敖，封于屈地（今湖北秭归）。屈氏正宗始祖（源流三：源于芈姓）。",
            },
            {
                "name": "屈原", "gender": "M",
                "courtesy_name": "名平，字灵均，号正则",
                "birth_date": "约前340年", "death_date": "约前278年",
                "birth_place": "楚国丹阳秭归",
                "notes": "春秋战国时期楚国大夫、诗人，被誉为「中华诗祖」「辞赋之祖」。创作《离骚》《九歌》《天问》等。端午节与其忠诚及悲壮结局相关。",
            },
            {
                "name": "屈突通", "gender": "M",
                "notes": "隋唐将领，初仕隋朝后归唐，忠诚勇猛。官至工部尚书，封蒋国公。",
            },
            {
                "name": "屈大均", "gender": "M",
                "courtesy_name": "字翁山，号泠君",
                "birth_date": "1630年", "death_date": "1696年",
                "birth_place": "广东番禺",
                "notes": "明末清初著名学者、诗人，与陈恭尹、梁佩兰并称「岭南三大家」。诗作反映社会现实，对岭南文学影响深远。",
            },
        ],
    },
    {
        "surname": "屈",
        "genealogy_name": "敦睦堂屈氏宗谱九卷首一卷",
        "region": "湖北罗田",
        "period": "民国9年(1920)四修",
        "volumes": "九卷首一卷，10册",
        "hall_name": "敦睦堂",
        "source_url": "https://www.zupu.cn/zhpk/46475",
        "founder_info": "远祖屈迥峰（江西南昌丰城），入楚祖屈子贯（避乱徙麻城），始迁祖屈栋材号大川（明由麻入罗田）。栋材下二子：屈廷鸾号奇峰、屈廷凤号金潭。",
        "collection_info": "太原市寻源姓氏文化研究中心；zupu.cn 在线。",
        "scattered_region": "湖北省罗田县等地",
        "description": "谱序题义水屈氏宗谱。字派(玉字后)：如汝立志 名达家邦 光昭先业 继述荣昌 扬清世绪 贻泽延长。",
        "generations": "如汝立志名达家邦光昭先业继述荣昌扬清世绪贻泽延长",
        "founders": [
            {"name": "屈迥峰", "gender": "M", "notes": "远祖，原籍江西南昌丰城县。"},
            {"name": "屈子贯", "gender": "M", "notes": "入楚祖，避乱徙麻城。"},
            {"name": "屈栋材", "gender": "M", "generation_number": 1, "courtesy_name": "号大川", "notes": "始迁祖，明由麻城入籍罗田。"},
            {"name": "屈廷鸾", "gender": "M", "generation_number": 2, "courtesy_name": "号奇峰", "notes": "栋材长子。"},
            {"name": "屈廷凤", "gender": "M", "generation_number": 2, "courtesy_name": "号金潭", "notes": "栋材次子。"},
        ],
    },
    {
        "surname": "屈",
        "genealogy_name": "雙峰屈氏五修宗譜",
        "region": "湖南湘乡、双峰",
        "period": "2003年刊",
        "volumes": "10卷",
        "hall_name": "惇叙堂",
        "source_url": "https://www.zupu.cn/zhpk/103834",
        "founder_info": "受姓祖瑕（武王子食采于屈）。江南远祖屈原。衡湘鼻祖屈𧏖（宋，占籍衡阳）。富圫始迁祖屈代鸾字友和（明由衡阳徙湘乡富圫）。鸾公三传分二支：屈名兴字祯楚、屈名富字荣楚。",
        "collection_info": "藏中国湖南图书馆。",
        "scattered_region": "湖南省湘乡县、双峰县等地",
        "description": "卷端题湘乡长塘屈氏五修宗谱。收藏者：中国湖南图书馆。",
        "founders": [
            {"name": "屈代鸾", "gender": "M", "courtesy_name": "字友和", "notes": "富圫始迁祖，明由衡阳徙湘乡富圫。"},
            {"name": "屈名兴", "gender": "M", "courtesy_name": "字祯楚", "notes": "鸾公三传后一支。"},
            {"name": "屈名富", "gender": "M", "courtesy_name": "字荣楚", "notes": "鸾公三传后一支。"},
        ],
    },
    {
        "surname": "屈",
        "genealogy_name": "湘鄉屈氏四修宗譜",
        "region": "湖南湘乡",
        "period": "民国32年(1943)",
        "volumes": "12卷",
        "hall_name": "惇敍堂",
        "source_url": "https://www.zupu.cn/zhpk/103835",
        "founder_info": "源流同雙峰五修。受姓祖瑕，江南远祖屈原。富圫始迁祖屈代鸾字友和（明）。",
        "collection_info": "藏中国湖南图书馆。",
        "scattered_region": "湖南省湘乡县等地",
        "description": "卷端题湘乡长塘屈氏四修宗谱。收藏者：中国湖南图书馆。",
        "founders": [
            {"name": "屈代鸾", "gender": "M", "courtesy_name": "字友和", "notes": "富圫始迁祖，明由衡阳徙湘乡富圫。"},
            {"name": "屈名兴", "gender": "M", "courtesy_name": "字祯楚", "notes": "鸾公三传后一支。"},
            {"name": "屈名富", "gender": "M", "courtesy_name": "字荣楚", "notes": "鸾公三传后一支。"},
        ],
    },
]


# ============================================================
# 贵州余庆屈氏族谱 —— 据 PDF 直系宗亲简图
# ============================================================
GUIZHOU = {
    "surname": "屈",
    "genealogy_name": "贵州余庆屈氏族谱",
    "region": "贵州余庆",
    "period": "现代整理",
    "volumes": None,
    "hall_name": None,
    "source_url": None,
    "founder_info": "始祖正四郎，一世屈开，直系传承至第25世凡字辈。",
    "collection_info": "民间整理，屈华（电话 13885225988）提供。",
    "scattered_region": "贵州省余庆县",
    "description": "据屈华统计整理（2024年6月）。直系宗亲简图自正四郎起，经屈开至第25世凡字辈，跨越约600年。",
}

GUIZHOU_LINEAGE = [
    (0, "正四郎", "始祖"),
    (1, "屈开", None),
    (2, "屈再四", None),
    (3, "屈值袋", None),
    (4, "屈景荣", None),
    (5, "屈纯", None),
    (6, "屈仲鸣", None),
    (7, "屈世英", None),
    (8, "屈兴才", None),
    (9, "屈宦", None),
    (10, "屈明伸", None),
    (11, "屈良惠", None),
    (12, "屈晴明", None),
    (13, "屈可问", None),
    (14, "屈之驿", None),
    (15, "屈启登", None),
    (16, "屈登芳", None),
    (17, "屈必成", None),
    (18, "屈自富", None),
    (19, "屈产聘", None),
    (20, "屈蘇山", None),
    (21, "屈常元", None),
    (22, "屈郡科", None),
]

GUIZHOU_BRANCHES = {
    "屈郡科": [
        {
            "gen": 23, "name": "屈慈洪", "children": [
                {"gen": 24, "name": "屈谷昭", "children": [
                    {"gen": 25, "name": "屈凡江"},
                ]},
                {"gen": 24, "name": "屈谷明", "children": [
                    {"gen": 25, "name": "屈容"},
                    {"gen": 25, "name": "屈进"},
                    {"gen": 25, "name": "屈华", "notes": "统计整理者"},
                    {"gen": 25, "name": "屈艳"},
                ]},
                {"gen": 24, "name": "屈谷英"},
                {"gen": 24, "name": "屈谷秀"},
                {"gen": 24, "name": "屈谷良", "children": [
                    {"gen": 25, "name": "屈凡宗"},
                    {"gen": 25, "name": "屈凡智"},
                    {"gen": 25, "name": "屈凡碧"},
                    {"gen": 25, "name": "屈凡刚"},
                    {"gen": 25, "name": "屈凡彪"},
                    {"gen": 25, "name": "屈仕海"},
                    {"gen": 25, "name": "屈凡娥"},
                    {"gen": 25, "name": "屈凡美"},
                    {"gen": 25, "name": "屈波"},
                    {"gen": 25, "name": "屈凡胜"},
                ]},
            ],
        },
        {"gen": 23, "name": "屈慈清"},
        {
            "gen": 23, "name": "屈慈元", "children": [
                {"gen": 24, "name": "屈谷喜", "children": [
                    {"gen": 25, "name": "屈凡飞"},
                    {"gen": 25, "name": "屈凡芳"},
                    {"gen": 25, "name": "屈凡春"},
                ]},
                {"gen": 24, "name": "屈谷珍"},
                {"gen": 24, "name": "屈谷平"},
            ],
        },
    ],
}


# ============================================================
# 主流程
# ============================================================
def run():
    with app.app_context():
        print("=" * 50)
        print("初始化数据库（推倒重建）")
        print("=" * 50)

        db.drop_all()
        db.create_all()
        print("表已重建。\n")

        # --- 1. 导入所有族谱 ---
        print("[1] 导入族谱 …")
        genealogy_map = {}
        for item in ALL_GENEALOGIES:
            g = GenealogyMain(
                surname=item["surname"],
                genealogy_name=item["genealogy_name"],
                region=item.get("region"),
                period=item.get("period"),
                volumes=item.get("volumes"),
                hall_name=item.get("hall_name"),
                source_url=item.get("source_url"),
                founder_info=item.get("founder_info"),
                collection_info=item.get("collection_info"),
                scattered_region=item.get("scattered_region"),
                description=item.get("description"),
            )
            db.session.add(g)
            db.session.flush()
            genealogy_map[item["genealogy_name"]] = g

            # 字辈
            gen_str = item.get("generations")
            if gen_str and isinstance(gen_str, str):
                for i, ch in enumerate(gen_str):
                    if ch.strip():
                        db.session.add(GenealogyGeneration(
                            genealogy_id=g.id, sort_order=i, character=ch,
                        ))

            # 始祖 / 名人成员
            for f in item.get("founders", []):
                m = FamilyMember(
                    genealogy_id=g.id,
                    name=f["name"],
                    gender=f.get("gender", "M"),
                    generation_number=f.get("generation_number"),
                    courtesy_name=f.get("courtesy_name"),
                    birth_date=f.get("birth_date"),
                    death_date=f.get("death_date"),
                    birth_place=f.get("birth_place"),
                    notes=f.get("notes"),
                )
                db.session.add(m)

            print(f"  + {g.genealogy_name}")

        # --- 2. 贵州余庆屈氏族谱（世系树） ---
        print("\n[2] 导入贵州余庆屈氏族谱及世系 …")
        gz = GenealogyMain(**{k: v for k, v in GUIZHOU.items() if v is not None})
        db.session.add(gz)
        db.session.flush()
        genealogy_map[gz.genealogy_name] = gz

        member_cache = {}

        def add_member(name, gen_num, father_id=None, notes=None):
            m = FamilyMember(
                genealogy_id=gz.id, name=name, gender="M",
                generation_number=gen_num, father_id=father_id,
                birth_place="贵州余庆", notes=notes,
            )
            db.session.add(m)
            db.session.flush()
            member_cache[name] = m
            return m

        prev_id = None
        for gen_num, name, notes in GUIZHOU_LINEAGE:
            m = add_member(name, gen_num, father_id=prev_id, notes=notes)
            prev_id = m.id

        def import_branch(items, parent_id):
            for item in items:
                m = add_member(item["name"], item["gen"], father_id=parent_id, notes=item.get("notes"))
                for child in item.get("children", []):
                    import_branch([child], m.id)

        for parent_name, branches in GUIZHOU_BRANCHES.items():
            parent = member_cache.get(parent_name)
            if parent:
                import_branch(branches, parent.id)

        gz_count = FamilyMember.query.filter_by(genealogy_id=gz.id).count()
        print(f"  + {gz.genealogy_name} ({gz_count} ren)")

        # --- 3. 敦睦堂父子关系补全 ---
        dunmu = genealogy_map.get("敦睦堂屈氏宗谱九卷首一卷")
        if dunmu:
            father = FamilyMember.query.filter_by(genealogy_id=dunmu.id, name="屈栋材").first()
            if father:
                for child_name in ("屈廷鸾", "屈廷凤"):
                    child = FamilyMember.query.filter_by(genealogy_id=dunmu.id, name=child_name).first()
                    if child:
                        child.father_id = father.id

        db.session.commit()

        # --- 统计 ---
        total_g = GenealogyMain.query.count()
        total_m = FamilyMember.query.count()
        total_gen = GenealogyGeneration.query.count()
        print(f"\n{'=' * 50}")
        print(f"完成！族谱 {total_g} 部 / 成员 {total_m} 人 / 字辈 {total_gen} 字")
        print("=" * 50)


if __name__ == "__main__":
    run()
