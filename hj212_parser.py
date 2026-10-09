class HJ212Parser:
    def _calc_crc16(self, data: bytes) -> int:
        """内部计算ANSI CRC16，初始0xFFFF，多项式0xA001（实验要求）"""
        crc = 0xFFFF
        poly = 0xA001
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
        return crc

    def is_valid_message(self, message: str) -> bool:
        """1.检查报文格式是否正确：##开头，\r\n结尾，长度合法"""
        if not isinstance(message, str):
            return False
        if not message.startswith("##"):
            return False
        if not message.endswith("\r\n"):
            return False
        if len(message) < 12:
            return False
        return True

    def validate_crc(self, message: str) -> bool:
        """2. 校验报文CRC值"""
        if not self.is_valid_message(message):
            return False
        # 截取待校验内容
        msg_body = message[2:-6]
        received_crc_hex = message[-6:-2]
        try:
            received_crc = int(received_crc_hex, 16)
        except ValueError:
            return False
        calc_crc = self._calc_crc16(msg_body.encode("gbk"))
        return calc_crc == received_crc

    def parse_data_segment(self, message: str) -> dict:
        """3.解析数据段，返回键值对字典"""
        if not self.is_valid_message(message):
            return {}
        length_str = message[2:6]
        data_len = int(length_str,10)
        data_start = 6
        data_end = 6 + data_len
        data_segment = message[data_start:data_end]
        result = {}
        items = data_segment.split(";")
        for item in items:
            if "=" in item:
                k, v = item.split("=",1)
                result[k.strip()] = v.strip()
        return result

    def extract_monitoring_data(self, message: str) -> dict:
        """4.从CP字段提取监测因子及数值"""
        data_dict = self.parse_data_segment(message)
        cp_content = data_dict.get("CP", "")
        monitor_data = {}
        if not cp_content:
            return monitor_data
        factors = cp_content.split(",")
        for factor in factors:
            if ":" in factor:
                name, val = factor.split(":",1)
                monitor_data[name.strip()] = val.strip()
        return monitor_data


# 测试代码（运行这个文件会打印结果，用来截图）
if __name__ == "__main__":
    parser = HJ212Parser()
    # 测试HJ212报文
    test_msg = "##0024QN=20240101120000;CP=pH:7.2,SO2:23.5\r\n"
    print("报文格式合法：", parser.is_valid_message(test_msg))
    print("CRC校验结果：", parser.validate_crc(test_msg))
    print("数据段解析结果：", parser.parse_data_segment(test_msg))
    print("监测因子数据：", parser.extract_monitoring_data(test_msg))
