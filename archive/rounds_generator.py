import random
from datetime import datetime, timedelta
import sys
import os

class DoctorRoundsGenerator:
    """
    病程记录框架生成器
    根据住院天数自动生成医生查房记录模板
    """
    
    # 医师信息
    DOCTORS = {
        'ATTENDING': '都吉香',
        'CHIEF': '车永生',
        'RESIDENT': '于友达'
    }
    
    # 查房类型枚举
    ROUNDS_TYPE = {
        'ATTENDING': '主治医师查房',
        'CHIEF': '主任医师查房',
        'RESIDENT': '住院医师查房',
        'SUMMARY': '阶段小结'
    }
    
    # 生命体征正常值范围
    VITAL_SIGNS_RANGE = {
        'TEMPERATURE': {'MIN': 36.2, 'MAX': 37.0, 'DECIMAL': 1},
        'PULSE': {'MIN': 65, 'MAX': 85, 'DECIMAL': 0},
        'RESPIRATION': {'MIN': 16, 'MAX': 19, 'DECIMAL': 0},
        'SYSTOLIC_BP': {'MIN': 110, 'MAX': 138, 'DECIMAL': 0},
        'DIASTOLIC_BP': {'MIN': 72, 'MAX': 88, 'DECIMAL': 0}
    }
    
    def __init__(self, admission_date, discharge_date):
        """
        初始化生成器
        
        :param admission_date: 入院日期，格式为'YYYY-MM-DD'
        :param discharge_date: 出院日期，格式为'YYYY-MM-DD'
        """
        self.admission_date = datetime.strptime(admission_date, '%Y-%m-%d')
        self.discharge_date = datetime.strptime(discharge_date, '%Y-%m-%d')
        self.total_days = (self.discharge_date - self.admission_date).days
    
    def _generate_random_time(self):
        """
        生成08:00到10:30之间的随机时间
        
        :return: 随机时间字符串，格式为'HH:MM'
        """
        hour = random.randint(8, 10)
        minute = random.randint(0, 59)
        
        # 如果小时是10点，分钟不能超过30分钟
        if hour == 10:
            minute = random.randint(0, 30)
            
        return f"{hour:02d}:{minute:02d}"
    
    def _generate_vital_signs(self):
        """
        生成正常范围内的随机生命体征数据
        
        :return: 生命体征字符串
        """
        # 生成各项生命体征数据
        temperature = round(random.uniform(
            self.VITAL_SIGNS_RANGE['TEMPERATURE']['MIN'],
            self.VITAL_SIGNS_RANGE['TEMPERATURE']['MAX']
        ), self.VITAL_SIGNS_RANGE['TEMPERATURE']['DECIMAL'])
        
        pulse = random.randint(
            self.VITAL_SIGNS_RANGE['PULSE']['MIN'],
            self.VITAL_SIGNS_RANGE['PULSE']['MAX']
        )
        
        respiration = random.randint(
            self.VITAL_SIGNS_RANGE['RESPIRATION']['MIN'],
            self.VITAL_SIGNS_RANGE['RESPIRATION']['MAX']
        )
        
        systolic_bp = random.randint(
            self.VITAL_SIGNS_RANGE['SYSTOLIC_BP']['MIN'],
            self.VITAL_SIGNS_RANGE['SYSTOLIC_BP']['MAX']
        )
        
        diastolic_bp = random.randint(
            self.VITAL_SIGNS_RANGE['DIASTOLIC_BP']['MIN'],
            self.VITAL_SIGNS_RANGE['DIASTOLIC_BP']['MAX']
        )
        
        return f"患者神志清，精神可。T：{temperature}°C，P：{pulse}次/分，R：{respiration}次/分，BP：{systolic_bp}/{diastolic_bp}mmHg。心肺等内科查体未见明确异常。"
    
    def _get_rounds_type(self, day):
        """
        根据住院天数确定查房类型
        
        :param day: 住院天数
        :return: 查房类型
        """
        # 阶段小结判断
        if day % 30 == 0:
            return self.ROUNDS_TYPE['SUMMARY']
        
        # 特殊日期处理
        if day == 2:
            return self.ROUNDS_TYPE['ATTENDING']
        elif day == 3:
            return self.ROUNDS_TYPE['CHIEF']
        elif day >= 6 and day % 3 == 0:  # 从第6天开始，每3天一个周期
            cycle_index = ((day - 6) // 3) % 3
            if cycle_index == 0:
                return self.ROUNDS_TYPE['RESIDENT']
            elif cycle_index == 1:
                return self.ROUNDS_TYPE['ATTENDING']
            else:  # cycle_index == 2
                return self.ROUNDS_TYPE['CHIEF']
        
        # 非查房日期
        return None
    
    def _handle_summary_conflict(self, day):
        """
        处理阶段小结与常规查房冲突的情况
        
        :param day: 住院天数
        :return: 实际的查房日期
        """
        if day % 30 == 0:  # 是阶段小结日
            # 检查该日是否也是常规查房日
            if self._get_rounds_type(day) is not None and self._get_rounds_type(day) != self.ROUNDS_TYPE['SUMMARY']:
                # 冲突，将常规查房顺延3天
                return day + 3
        return day
    
    def _generate_rounds_record(self, day, rounds_type):
        """
        生成查房记录框架
        
        :param day: 住院天数
        :param rounds_type: 查房类型
        :return: 查房记录框架字符串
        """
        # 计算查房日期
        rounds_date = self.admission_date + timedelta(days=day-1)
        date_str = rounds_date.strftime('%Y-%m-%d')
        time_str = self._generate_random_time()
        
        # 生成记录标题
        if rounds_type == self.ROUNDS_TYPE['SUMMARY']:
            # 阶段小结只需要标题
            record = f"{date_str} {time_str} {rounds_type}记录"
            return record
        elif rounds_type == self.ROUNDS_TYPE['ATTENDING']:
            record = f"{date_str} {time_str} {self.DOCTORS['ATTENDING']}{self.ROUNDS_TYPE['ATTENDING']}记录\n"
        elif rounds_type == self.ROUNDS_TYPE['CHIEF']:
            record = f"{date_str} {time_str} {self.DOCTORS['CHIEF']}{self.ROUNDS_TYPE['CHIEF']}记录\n"
        else:  # 住院医师查房
            record = f"{date_str} {time_str} {self.ROUNDS_TYPE['RESIDENT']}记录\n"
        
        # 添加记录正文内容
        # 主治医师和主任医师查房有"汇报病史略"
        if rounds_type in [self.ROUNDS_TYPE['ATTENDING'], self.ROUNDS_TYPE['CHIEF']]:
            record += "汇报病史略\n"
        
        # 主诉内容（框架）
        record += "主诉：\n"
        
        # 查体内容（包含随机生命体征）
        record += self._generate_vital_signs() + "\n"
        
        # 上级医师分析
        record += "上级医师分析：\n"
        
        # 家属宣教
        record += "家属宣教：\n"
        
        # 签名
        if rounds_type == self.ROUNDS_TYPE['RESIDENT']:
            record += f"\n住院医师：{self.DOCTORS['RESIDENT']}"
        elif rounds_type == self.ROUNDS_TYPE['ATTENDING']:
            record += f"\n住院医师：{self.DOCTORS['RESIDENT']}\n主治医师：{self.DOCTORS['ATTENDING']}"
        elif rounds_type == self.ROUNDS_TYPE['CHIEF']:
            record += f"\n住院医师：{self.DOCTORS['RESIDENT']}\n主任医师：{self.DOCTORS['CHIEF']}"
        else:
            record += f"\n医师签名："
        
        return record
    
    def generate_all_rounds_records(self):
        """
        生成所有查房记录框架
        
        :return: 查房记录框架列表
        """
        records = []
        
        # 从第2天开始生成记录（第1天为入院记录，不需要程序生成）
        for day in range(2, self.total_days + 2):
            # 获取查房类型
            rounds_type = self._get_rounds_type(day)
            
            # 如果是阶段小结日且与常规查房冲突，处理冲突
            actual_day = self._handle_summary_conflict(day)
            
            # 如果是查房日，生成记录
            if rounds_type is not None:
                record = self._generate_rounds_record(day, rounds_type)
                records.append({
                    'day': day,
                    'date': (self.admission_date + timedelta(days=day-1)).strftime('%Y-%m-%d'),
                    'type': rounds_type,
                    'record': record
                })
        
        return records

def get_date_input(prompt):
    """
    获取用户输入的日期，并验证格式
    
    :param prompt: 提示信息
    :return: 验证后的日期字符串
    """
    while True:
        try:
            date_str = input(prompt)
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("日期格式错误，请使用 YYYY-MM-DD 格式，例如：2025-08-03")

def save_records_to_file(records, admission_date, discharge_date, output_dir="records"):
    """
    将所有查房记录保存到一个文件中
    
    :param records: 查房记录列表
    :param admission_date: 入院日期
    :param discharge_date: 出院日期
    :param output_dir: 输出目录
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成文件名
    filename = f"{admission_date}_{discharge_date}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # 保存所有记录到一个文件
    with open(filepath, 'w', encoding='utf-8') as f:
        for i, record in enumerate(records):
            f.write(record['record'])
            # 如果不是最后一条记录，则添加分隔符
            if i < len(records) - 1:
                f.write("\n\n")
    
    print(f"所有记录已保存到 {filepath}")

def main():
    """
    主函数，演示如何使用病程记录框架生成器
    """
    # 获取用户输入
    print("病程记录框架生成器")
    print("-" * 30)
    
    admission_date = get_date_input("请输入入院日期 (格式: YYYY-MM-DD): ")
    discharge_date = get_date_input("请输入出院日期 (格式: YYYY-MM-DD): ")
    
    try:
        # 检查日期逻辑
        admission = datetime.strptime(admission_date, '%Y-%m-%d')
        discharge = datetime.strptime(discharge_date, '%Y-%m-%d')
        
        if discharge <= admission:
            print("错误：出院日期必须晚于入院日期")
            sys.exit(1)
        
        # 创建生成器实例
        generator = DoctorRoundsGenerator(admission_date, discharge_date)
        records = generator.generate_all_rounds_records()
        
        # 显示生成的记录数量
        print(f"\n共生成 {len(records)} 条查房记录框架\n")
        
        # 直接保存到records目录
        save_records_to_file(records, admission_date, discharge_date, "records")
            
    except ValueError as e:
        print(f"日期格式错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()