

def calculator_tool(expression):
   """
   计算数学表达式,仅仅支持+,-,*,/四则运算和括号。
   :param expression: 数学表达式字符串
   :return: 计算结果
   """
   try:
    eval(expression, {"__builtins__": None}, {})
    return f"计算结果: {eval(expression)}"
   except Exception as e:
    print(e)
   return "Invalid expression"
