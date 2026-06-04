import json
import random
import os

class GameState:
    """游戏状态管理类"""
    
    def __init__(self):
        """初始化游戏状态，加载角色数据"""
        # 获取当前文件所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"GameState 初始化，base_dir: {self.base_dir}")
        
        # 尝试多个可能的数据目录路径
        self.data_dir = self._find_data_dir()
        print(f"数据目录: {self.data_dir}")
        
        self.roles_data = self._load_roles()
        self.clues_data = self._load_clues()
        self.stage_openings = self._load_stage_openings()
        self.current_stage = 1
        self.ap_points = 10
        self.unlocked_clues = []
    
    def _find_data_dir(self):
        """查找数据目录，尝试多个可能的路径"""
        possible_paths = [
            os.path.join(self.base_dir, 'data'),
            os.path.join(os.getcwd(), 'data'),
            'data',
            os.path.join(os.path.dirname(os.path.dirname(self.base_dir)), 'data'),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            print(f"检查数据目录: {abs_path}")
            if os.path.isdir(abs_path):
                print(f"找到数据目录: {abs_path}")
                return abs_path
        
        print(f"未找到数据目录，使用默认路径: {possible_paths[0]}")
        return possible_paths[0]
    
    def _get_data_path(self, filename):
        """获取数据文件的绝对路径"""
        return os.path.join(self.data_dir, filename)
    
    def _load_roles(self):
        """加载角色数据"""
        try:
            filepath = self._get_data_path('roles.json')
            print(f"尝试加载角色数据: {filepath}")
            print(f"文件是否存在: {os.path.exists(filepath)}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                roles = data.get('roles', [])
                print(f"成功加载角色数据，共 {len(roles)} 个角色")
                return roles
        except Exception as e:
            print(f"加载角色数据失败: {type(e).__name__}: {e}")
            # 返回默认角色数据作为备用
            return self._get_default_roles()
    
    def _get_default_roles(self):
        """返回默认角色数据（备用方案）"""
        print("使用默认角色数据")
        return [
            {"id": "lin_shen", "name": "林深", "profession": "结构工程师", "age": 26, "description": "严成的得意门生，技术纯粹，对导师有深厚感情。性格严谨但略显稚嫩。", "photo": "", "goal": "查明导师坠海真相，验证4号墩结构安全性，洗清自己的设计嫌疑。", "key_secrets": [], "scripts": {"act_1": "", "act_2": "", "act_3": ""}},
            {"id": "gu_yuan", "name": "顾远", "profession": "岩土工程师", "age": 50, "description": "老牌技术专家，固执正直。与死者严成是多年老友。", "photo": "", "goal": "揭露地质数据造假，查明严成背叛理想的真相，保护大桥根基。", "key_secrets": [], "scripts": {"act_1": "", "act_2": "", "act_3": ""}},
            {"id": "zhao_tai", "name": "赵泰", "profession": "甲方代表", "age": 30, "description": "资本代理人，极端理性，视工程为金钱游戏。心思缜密，精通物理逻辑。", "photo": "", "goal": "掩盖八百万贪污款项，将严成彻底封入桩基。", "key_secrets": [], "scripts": {"act_1": "", "act_2": "", "act_3": ""}},
            {"id": "xia_he", "name": "夏禾", "profession": "造价工程师", "age": 24, "description": "职场精英，追求物欲。在金钱诱惑下沦为赵泰的共犯。", "photo": "", "goal": "平掉账目缺口，销毁监控证据，洗清自身关联。", "key_secrets": [], "scripts": {"act_1": "", "act_2": "", "act_3": ""}},
            {"id": "su_xiao", "name": "苏晓", "profession": "材料实验员", "age": 23, "description": "职场新人，胆小且良知未泯。对严成心存感激。", "photo": "", "goal": "通过实验数据还原真相，寻找自我救赎。", "key_secrets": [], "scripts": {"act_1": "", "act_2": "", "act_3": ""}},
        ]
    
    def _load_clues(self):
        """加载线索数据"""
        try:
            filepath = self._get_data_path('clue.json')
            print(f"尝试加载线索数据: {filepath}")
            print(f"文件是否存在: {os.path.exists(filepath)}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功加载线索数据，共 {sum(len(clues) for clues in data.values())} 条线索")
                return data
        except Exception as e:
            print(f"加载线索数据失败: {type(e).__name__}: {e}")
            # 返回默认线索数据作为备用
            return self._get_default_clues()
    
    def _get_default_clues(self):
        """返回默认线索数据（备用方案）"""
        print("使用默认线索数据")
        return {
            "scene_clues": [
                {"id": "场01", "name": "断裂的A支点钢钎", "description": "断面极其平整，没有受力拉伸的颈缩现象。切口边缘在灯光下有晶体状的反光。", "logic_hint": "证明是脆性断裂，指向超低温影响。", "ap_cost": 1},
                {"id": "场02", "name": "残留的白霜", "description": "在支架断裂的缝隙中，仍能看到一层未融化的白霜。", "logic_hint": "证明现场曾出现过极低温物体。", "ap_cost": 1},
                {"id": "场03", "name": "平台监控摄像头", "description": "镜头完好，但保险丝有人为灼烧痕迹。", "logic_hint": "证明监控失效是人为破坏。", "ap_cost": 1},
                {"id": "场04", "name": "泥浆池样本", "description": "泥浆呈现深灰色，质地极其粘稠。", "logic_hint": "解释了死者为何瞬间沉底。", "ap_cost": 1}
            ],
            "object_clues": [
                {"id": "物01", "name": "蓝色金属罐（空）", "description": "罐体标注为工业液氮。", "logic_hint": "关键凶器。", "ap_cost": 2},
                {"id": "物02", "name": "废料桶里的试块", "description": "混凝土试块压力值未达标。", "logic_hint": "揭露工程质量造假。", "ap_cost": 2},
                {"id": "物03", "name": "微型手持磨光机", "description": "刀片上有金属碎屑。", "logic_hint": "证明钢钎被预先切割。", "ap_cost": 2},
                {"id": "物04", "name": "领用记录", "description": "液氮罐钥匙被取走未还。", "logic_hint": "锁定作案准备时间线。", "ap_cost": 1}
            ],
            "document_clues": [
                {"id": "文01", "name": "地勘复核报告", "description": "溶洞深度数据被缩减。", "logic_hint": "证明数据造假。", "ap_cost": 1},
                {"id": "文02", "name": "转账底单", "description": "款项流向不明公司。", "logic_hint": "核心杀人动机。", "ap_cost": 1},
                {"id": "文03", "name": "举报信残页", "description": "严成提到赵泰多次索要液氮钥匙。", "logic_hint": "反向锁定凶器。", "ap_cost": 2}
            ],
            "private_clues": [
                {"id": "深01", "name": "计算器记录", "description": "钢钎临界承载力计算记录。", "logic_hint": "还原杀人陷阱。", "ap_cost": 2},
                {"id": "深02", "name": "手机短信", "description": "赵泰指令夏禾拉闸的短信。", "logic_hint": "坐实预谋杀人。", "ap_cost": 3},
                {"id": "深03", "name": "金属碎片", "description": "带有冷脆纹路的金属碎片。", "logic_hint": "证明液氮冷脆存在。", "ap_cost": 2}
            ]
        }
    
    def _load_stage_openings(self):
        """加载阶段开场台词"""
        try:
            filepath = self._get_data_path('stage_openings.json')
            print(f"尝试加载阶段开场台词: {filepath}")
            print(f"文件是否存在: {os.path.exists(filepath)}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功加载阶段开场台词，共 {len(data)} 个阶段")
                return data
        except Exception as e:
            print(f"加载阶段开场台词失败: {type(e).__name__}: {e}")
            # 返回默认阶段开场台词作为备用
            return self._get_default_stage_openings()
    
    def _get_default_stage_openings(self):
        """返回默认阶段开场台词（备用方案）"""
        print("使用默认阶段开场台词")
        return {
            "stage_1": "各位，欢迎来到伶仃洋。现在是2026年3月27日。\n在你们脚下，是耗资百亿的S大桥4号主塔墩。它是整座大桥的脊梁，也是你们这半年来赖以生存的孤岛。\n工程界的规矩：桩基入岩，分毫不差。但在今晚，这个规矩碎了。\n半小时前，4号施工平台发生倾斜，项目总工严成坠入百米深的泥浆池，瞬间失踪。\n现在，由于风浪过大，交通船无法靠岸，你们五个人被困在这座孤岛上。\n在救援到来前的这四个小时里，我们需要聊聊：\n**为什么一根设计冗余充足的钢钎会突然脆断？为什么原本该救命的泥浆变成了杀人的陷阱？**\n各位工程师、造价师，请翻开你们的剧本。\n记住，大桥不说话，但数据会报复。",
            "stage_2": "第一阶段搜证开启。\n在这个环节，你们会发现4号墩不仅仅是一座桥墩，它是一张布满谎言的滤网。\n林深，去看看你师父那些被粉碎的图纸；顾远，去闻闻那岩芯里的海盐味；夏禾、苏晓，你们手里的笔，真的只写过真相吗？\n请各位根据线索，讨论出一个核心问题：**严成在死前，到底抓住了谁的辫子？**",
            "stage_3": "时间不多了。泥浆正在凝固，灌注已经开始。\n一旦混凝土封顶，严成的尸体将永远成为桩基的一部分。\n赵泰，你说是设计失误；林深，你说是材料造假。\n但我要提醒各位：\n**泥浆的比重不会骗人，液氮的余温不会骗人，删除的监控记录更不会骗人。**\n现在，请投出你们的一票。谁，才是那个利用物理学进行处刑的刽子手？",
            "stage_4": "所有证据已经齐全，现在进入最终复盘。让我为你们讲述这个案件完整的故事——从液氮如何使钢筋脆化，到泥浆比重如何被操控，再到凶手是如何一步步实施这个精密计划的。这不仅是一个谋杀案，更是一个关于工程伦理的悲剧。"
        }
    
    def get_stage_opening(self, stage):
        """获取指定阶段的开场台词
        
        Args:
            stage: 游戏阶段（1-4）
            
        Returns:
            str: 阶段开场台词
        """
        key = f"stage_{stage}"
        return self.stage_openings.get(key, "")
    
    def get_character_hint(self, character_id, stage):
        """根据角色ID和游戏阶段获取提示
        
        Args:
            character_id: 角色ID
            stage: 游戏阶段（1-4）
            
        Returns:
            str: 角色对应的剧本内容提示
        """
        # 找到对应角色
        for role in self.roles_data:
            if role.get('id') == character_id:
                # 根据阶段获取对应剧本
                scripts = role.get('scripts', {})
                if stage == 1:
                    return scripts.get('act_1', '')
                elif stage == 2:
                    return scripts.get('act_2', '')
                elif stage == 3:
                    return scripts.get('act_3', '')
                elif stage == 4:
                    # 第四阶段返回角色的目标
                    return role.get('goal', '')
        return "未找到对应角色或阶段的提示"
    
    def get_all_roles(self):
        """获取所有角色信息
        
        Returns:
            list: 角色信息列表
        """
        return self.roles_data
    
    def get_role_by_id(self, character_id):
        """根据ID获取角色信息
        
        Args:
            character_id: 角色ID
            
        Returns:
            dict: 角色信息
        """
        for role in self.roles_data:
            if role.get('id') == character_id:
                return role
        return None
    
    def next_stage(self):
        """推进到下一阶段
        
        Returns:
            int: 新的阶段
        """
        if self.current_stage < 4:
            self.current_stage += 1
        return self.current_stage
    
    def unlock_clue(self, prompt):
        """根据提示解锁线索
        
        Args:
            prompt: 用户输入的提示
            
        Returns:
            dict or str: 解锁的线索或提示信息
        """
        all_clues = []
        
        # 收集所有线索
        for clue_type, clues in self.clues_data.items():
            all_clues.extend(clues)
        
        # 过滤已解锁的线索
        available_clues = [clue for clue in all_clues if clue['id'] not in [c['id'] for c in self.unlocked_clues]]
        
        if not available_clues:
            return "当前没有可搜索的线索"
        
        # 关键词匹配
        keyword_clues = []
        keywords = ['现场', '断口', '碎片', '样本', '监控', '泥浆', '液氮', '磨光机', '记录', '报告', '转账', '举报信']
        
        for clue in available_clues:
            clue_text = f"{clue['name']} {clue['description']}"
            for keyword in keywords:
                if keyword in clue_text and prompt.find(keyword) != -1:
                    keyword_clues.append(clue)
                    break
        
        if keyword_clues:
            clue = random.choice(keyword_clues)
        else:
            # 随机返回一个可用线索
            clue = random.choice(available_clues)
        
        # 检查AP点数是否足够
        if self.ap_points >= clue['ap_cost']:
            self.ap_points -= clue['ap_cost']
            self.unlocked_clues.append(clue)
            return clue
        else:
            return "AP点数不足"
    
    def get_truth(self):
        """获取真相复盘
        
        Returns:
            str: 真相复盘内容
        """
        try:
            filepath = self._get_data_path('truth.txt')
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"加载真相复盘失败: {type(e).__name__}: {e}")
            return ""

