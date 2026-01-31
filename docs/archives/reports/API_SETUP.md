# API配置说明

## 已配置的AI服务

### 魔搭社区 (ModelScope)
- **API密钥**: `ms-f449b8b0-f623-4f91-9288-a1c13d38daed`
- **模型**: `deepseek-ai/DeepSeek-V3`
- **Base URL**: `https://api.modelscope.cn/v1`

### 硅基流动 (SiliconFlow) - 嵌入服务
- **API密钥**: `sk-tweswtuyrbzxxjiziprqrqchpkiwyxapctgaqutocucsptqx`
- **模型**: `BAAI/bge-large-zh-v1.5`
- **用途**: 文本向量化，用于知识库语义检索

## 测试API连接

运行测试脚本：
```bash
python test_api.py
```

## 配置文件位置

配置已保存在 `config.json`：
```json
{
  "ai_services": {
    "default": "modelscope",
    "modelscope": {
      "api_key": "ms-f449b8b0-f623-4f91-9288-a1c13d38daed",
      "model": "deepseek-ai/DeepSeek-V3",
      "base_url": "https://api.modelscope.cn/v1"
    }
  }
}
```

## 使用说明

1. **启动应用**
   ```bash
   python main.py
   ```

2. **API已配置完成**
   - 患者信息提取
   - 病程记录生成
   - 康复计划生成

3. **知识库功能**
   - 硅基流动API用于文档向量化
   - 支持PDF/EPUB/Word文档导入
   - 语义检索相关内容

## 注意事项

- API密钥已配置，无需额外设置
- 确保网络连接正常
- 如果API调用失败，检查密钥是否有效

## 故障排查

如果遇到连接错误：
1. 检查网络连接
2. 验证API密钥是否有效
3. 确认模型名称正确
4. 运行测试脚本诊断：`python test_api.py`
