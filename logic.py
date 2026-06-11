import json
import random

class GameState:
    """游戏状态管理类"""
    
    def __init__(self):
        """初始化游戏状态，加载角色数据"""
        self.roles_data = self._load_roles()
        self.clues_data = self._load_clues()
        self.stage_openings = self._load_stage_openings()
        self.current_stage = 1
        self.ap_points = 10
        self.unlocked_clues = []
        self.current_role_id = None
    
    def set_current_role(self, role_id):
        """设置当前角色"""
        self.current_role_id = role_id
    
    def _load_roles(self):
        """加载角色数据"""
        try:
            with open('data/roles.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('roles', [])
        except Exception as e:
            print(f"加载角色数据失败: {e}")
            return []
    
    def _load_clues(self):
        """加载线索数据"""
        try:
            with open('data/clue.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载线索数据失败: {e}")
            return {}
    
    def _load_stage_openings(self):
        """加载阶段开场台词"""
        try:
            with open('data/stage_openings.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载阶段开场台词失败: {e}")
            return {}
    
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
        """根据提示解锁线索（每个角色只能解锁自己分配的线索，按顺序解锁）
        
        Args:
            prompt: 用户输入的提示
            
        Returns:
            dict or str: 解锁的线索或提示信息
        """
        all_clues = []
        
        # 收集所有线索
        for clue_type, clues in self.clues_data.items():
            all_clues.extend(clues)
        
        # 获取当前角色的分配线索
        assigned_clue_ids = []
        if self.current_role_id:
            role = self.get_role_by_id(self.current_role_id)
            if role and 'assigned_clues' in role:
                assigned_clue_ids = role['assigned_clues']
        
        # 过滤已解锁的线索，并且只保留当前角色分配的线索
        if assigned_clue_ids:
            available_clues = [
                clue for clue in all_clues 
                if clue['id'] not in [c['id'] for c in self.unlocked_clues]
                and clue['id'] in assigned_clue_ids
            ]
        else:
            available_clues = [clue for clue in all_clues if clue['id'] not in [c['id'] for c in self.unlocked_clues]]
        
        if not available_clues:
            return "当前没有可搜索的线索"
        
        # 关键词精确匹配
        keyword_clues = []
        keywords = ['现场', '断口', '碎片', '样本', '监控', '泥浆', '液氮', '磨光机', '记录', '报告', '转账', '举报信']
        
        for clue in available_clues:
            clue_text = f"{clue['name']} {clue['description']}"
            for keyword in keywords:
                if keyword in clue_text and prompt.find(keyword) != -1:
                    keyword_clues.append(clue)
                    break
        
        if keyword_clues:
            # 如果有多个匹配，返回第一个匹配的线索
            clue = keyword_clues[0]
        else:
            # 按分配顺序返回下一个未解锁的线索
            clue = None
            for clue_id in assigned_clue_ids:
                if clue_id not in [c['id'] for c in self.unlocked_clues]:
                    for c in all_clues:
                        if c['id'] == clue_id:
                            clue = c
                            break
                    if clue:
                        break
        
        if not clue:
            return "当前没有可搜索的线索"
        
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
            with open('data/truth.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"加载真相复盘失败: {e}")
            return ""

