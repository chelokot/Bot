import time, random
default_print = print
def print(*args, **kwargs):
    default_print(*args, **kwargs)
    while True:
        try:
            f = open('/home/andrew/var/log/main_log.txt', 'a+')
            f.write(str(args) + '\n')
            f.close()
            break
        except:
            time.sleep(random.random())

from typing import List

import math
ops = [["^"], ["*", "/", "|"], ["%"], ["+", "-"], ["<", ">", "<=", ">=", "==", "!="], ['and'], ['or']]
ops_lambdas = {
    "^": lambda a, b: a ** b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "|": lambda a, b: a // b,
    "%": lambda a, b: a % b,
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b,
}

import requests, json
def get(url: str, params: dict) -> dict:
    print(f"Get input: {url}, {params}")
    return json.loads(requests.get(url, params).text)

default_functions = ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs', 'ln', 'get']
default_functions_lambdas = {
    'sin': lambda a: math.sin(a),
    'cos': lambda a: math.cos(a),
    'tan': lambda a: math.tan(a),
    'exp': lambda a: math.exp(a),
    'log': lambda a: math.log(a),
    'sqrt': lambda a: math.sqrt(a),
    'abs': lambda a: abs(a),
    'ln': lambda a: math.log(a),
    'get': lambda a: get(a, {}),
}

def expression_eval(tokens: List[str], functions, functions_lambdas) -> float:
    print(f"Eval input: {tokens}")
    if tokens[0] == '/' or tokens[0] == '-':
        return 1/0
    first_parenthesis = -1
    for i in range(len(tokens)):
        if tokens[i] == "(":
            first_parenthesis = i
            break
    if first_parenthesis != -1:
        matching_parenthesis = -1
        parenthesis_count = 1
        for i in range(first_parenthesis + 1, len(tokens)):
            if tokens[i] == "(":
                parenthesis_count += 1
            elif tokens[i] == ")":
                parenthesis_count -= 1
            if parenthesis_count == 0:
                matching_parenthesis = i
                break
        sub_tokens = tokens[first_parenthesis + 1:matching_parenthesis]
        sub_result = expression_eval(sub_tokens, functions, functions_lambdas)
        return expression_eval(tokens[:first_parenthesis] + [str(sub_result)] + tokens[matching_parenthesis + 1:], functions, functions_lambdas)
    # No parenthesis
    for function in functions:
        for i in range(len(tokens)):
            if tokens[i] == function:
                if(len(tokens) == 1):
                    return function
                arg = expression_eval([tokens[i+1]], functions, functions_lambdas)
                if type(arg) == str and arg[0] == '"':
                    arg = arg[1:-1]
                result = functions_lambdas[function](arg)
                if type(result) == list or type(result) == dict:
                    new_variable_name = f"__{function}_{random.randint(0, 1000000)}__"
                    while new_variable_name in functions:
                        new_variable_name = f"__{function}_{random.randint(0, 1000000)}__"
                    functions.append(new_variable_name)
                    functions_lambdas[new_variable_name] = lambda a: result[a]
                    return expression_eval(tokens[:i] + [new_variable_name] + tokens[i+2:], functions, functions_lambdas)
                else:
                    return expression_eval(tokens[:i] + [str(result)] + tokens[i+2:], functions, functions_lambdas)
    # No functions
    for op_priority in ops:
        for i in range(len(tokens)):
            if tokens[i] in op_priority:
                return expression_eval(tokens[:i-1] + [str(ops_lambdas[tokens[i]](expression_eval([tokens[i-1]], functions, functions_lambdas), expression_eval([tokens[i+1]], functions, functions_lambdas)))] + tokens[i+2:], functions, functions_lambdas)
    # No operators
    if tokens[0] == '':
        return ''
    if tokens[0][0] != '"':
        try:
            f = float(tokens[0])
            if (f == int(f)):
                return int(f)
            return f
        except ValueError:
            if tokens[0] == "True":
                return True
            elif tokens[0] == "False":
                return False
            else:
                return tokens[0]
    else:
        return tokens[0]

def number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

def parse(expression: str) -> List[str]:
    print(f"Parse input: {expression}")
    tokens = []
    current_token = ""
    for c in expression:
        if c == " ":
            if current_token != "":
                tokens.append(current_token)
                current_token = ""
        elif c in "0123456789.":
            current_token += c
        else:
            if(number(current_token)):
                tokens.append(current_token)
                current_token = ""
            if '"' not in current_token and c in "()+-*/^%|<>":
                if current_token != "":
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(c)
            elif '"' not in current_token and len(current_token) > 0 and (current_token[-1] == "<" and c == "=" or current_token[-1] == ">" and c == "=" or current_token[-1] == "=" and c == "=" or current_token[-1] == "!" and c == "=" or current_token[-1] == "o" and c == "r"):
                if len(current_token) > 1:
                    tokens.append(current_token[:-1])
                tokens.append(current_token[-1] + c)
                current_token = ""
            elif '"' not in current_token and len(current_token) > 1 and (current_token[-2:] == "an" and c == "d"):
                if len(current_token) > 2:
                    tokens.append(current_token[:-2])
                tokens.append(current_token[-2:] + c)
                current_token = ""
            elif c == '"' and '"' in current_token:
                tokens.append(current_token + c)
                current_token = ""
            else:
                current_token += c
    if current_token != "":
        tokens.append(current_token)
    print(f"Parse output: {tokens}")
    return tokens

from typing import Dict
from copy import deepcopy
def execute_program(
        program_code: str, 
        variables: Dict[str, str], 
        message, 
        functions = None, 
        functions_lambdas = None, 
        global_variables = None,
        user_variables = None,
        ) -> str:
    print(f"Execute input: {program_code}, {variables}")
    if 'return' in variables.keys():
        if type(variables['return']) != str:
            return str(variables['return'])
        return variables['return'].replace('"', '')
    if program_code == "":
        return ""
    
    if functions == None:
        functions = deepcopy(default_functions)
    if functions_lambdas == None:
        functions_lambdas = deepcopy(default_functions_lambdas)

    clear = lambda s: s.replace("\n", ";").replace("\t", "").replace(" ", "").replace("'", '"')
    clear_with_dollars = '$'.join([clear(line) if i % 2 == 0 else line for i, line in enumerate(program_code.split('$'))])
    program_code = '"'.join([clear_with_dollars(line) if i % 2 == 0 else line for i, line in enumerate(program_code.split('"'))])
    if program_code[-1] != ";":
        program_code += ";"

    print(f"Cleared: {program_code}")
    
    if program_code.startswith("if"):
        matching_parenthesis = -1
        parenthesis_count = 1
        for i in range(3, len(program_code)):
            if program_code[i] == "(":
                parenthesis_count += 1
            elif program_code[i] == ")":
                parenthesis_count -= 1
            if parenthesis_count == 0:
                matching_parenthesis = i
                break
        condition = program_code[3:matching_parenthesis]
        
        first_subprogram_start = matching_parenthesis + 1
        first_subprogram_end = -1
        parenthesis_count = 0
        for i in range(first_subprogram_start, len(program_code)):
            if program_code[i] == "{":
                parenthesis_count += 1
            elif program_code[i] == "}":
                parenthesis_count -= 1
            if parenthesis_count == 0:
                first_subprogram_end = i
                break
        first_subprogram = program_code[first_subprogram_start + 1:first_subprogram_end]

        execute_second = False
        if expression_eval(parse(substitute_variables(condition, variables, message, global_variables, user_variables)), functions, functions_lambdas):
            print("Condition is true, executing first subprogram")
            execute_program(first_subprogram, variables, message, functions, functions_lambdas, global_variables, user_variables)
        else:
            print("Condition is false")
            execute_second = True
        
        if program_code[first_subprogram_end + 1:].startswith("else"):
            second_subprogram_start = first_subprogram_end + 5
            second_subprogram_end = -1
            parenthesis_count = 1
            for i in range(second_subprogram_start + 1, len(program_code)):
                if program_code[i] == "{":
                    parenthesis_count += 1
                elif program_code[i] == "}":
                    parenthesis_count -= 1
                if parenthesis_count == 0:
                    second_subprogram_end = i
                    break
            second_subprogram = program_code[second_subprogram_start + 1:second_subprogram_end]
            if execute_second:
                print("Executing second subprogram")
                execute_program(second_subprogram, variables, message, functions, functions_lambdas, global_variables, user_variables)
            print("Finished executing if")
            return execute_program(program_code[second_subprogram_end + 1:], variables, message, functions, functions_lambdas, global_variables, user_variables)
        else:
            print("Finished executing if")
            return execute_program(program_code[ first_subprogram_end + 1:], variables, message, functions, functions_lambdas, global_variables, user_variables)
            
    # starts with command
    command = program_code[:program_code.index(";")]
    execute_command(command, variables, message, functions, functions_lambdas, global_variables, user_variables)
    return execute_program(program_code[program_code.index(";") + 1:], variables, message, functions, functions_lambdas, global_variables, user_variables)

def substitute_variables(
        expression: str, 
        variables: Dict[str, str], 
        message,
        global_variables: Dict[str, str],
        user_variables: Dict[str, str],
        ) -> str:
    print(f"Substitute input: {expression}, {variables}")
    for variable in variables.keys():
        if(type(variables[variable]) != list and type(variables[variable]) != dict):
            if(type(variables[variable]) == str):
                expression = expression.replace(f"${variable}$", f'{variables[variable]}')
            else:
                expression = expression.replace(f"${variable}$", str(variables[variable]))
    for global_variable in global_variables.keys():
        if(type(global_variables[global_variable]) != list and type(global_variables[global_variable]) != dict):
            if(type(global_variables[global_variable]) == str):
                expression = expression.replace(f"$global {global_variable}$", f'{global_variables[global_variable]}')
            else:
                expression = expression.replace(f"$global {global_variable}$", str(global_variables[global_variable]))
    for user_variable in user_variables.keys():
        if(type(user_variables[user_variable]) != list and type(user_variables[user_variable]) != dict):
            if(type(user_variables[user_variable]) == str):
                expression = expression.replace(f"$user {user_variable}$", f'{user_variables[user_variable]}')
            else:
                expression = expression.replace(f"$user {user_variable}$", str(user_variables[user_variable]))
    print(f"Substitute variables output: {expression}")
    while "$message." in expression:
        message_substitution_start = expression.index("$message.")
        message_substitution_end = -1
        for i in range(message_substitution_start + 1, len(expression)):
            if expression[i] == "$":
                message_substitution_end = i
                break
        message_substitution = expression[message_substitution_start + 1:message_substitution_end]
        # check that message only contains letters, numbers and dots
        if not all(c.isalnum() or c == "." or c == "_" for c in message_substitution):
            raise Exception("Message substitution contains illegal characters: " + message_substitution)
        message_substituted = eval(message_substitution)
        expression = expression[:message_substitution_start] + str(message_substituted) + expression[message_substitution_end + 1:]
    print(f"Substitute message output: {expression}")
    return expression

import regex
def process_assignment_expression(expression: str, functions, functions_lambdas):
    if expression[0] == '"':
        return expression[1:-1]
    elif expression[0] == "[":
        # (possibly nested) list
        elems_string = expression[1:-1]
        elems = []
        elem = ''
        in_str = False

        square_brackets_count = 0
        curly_brackets_count = 0

        for char in elems_string:
            if char == '"':
                in_str = not in_str
            if char == "[" and not in_str:
                square_brackets_count += 1
            if char == "]" and not in_str:
                square_brackets_count -= 1
            if char == "{" and not in_str:
                curly_brackets_count += 1
            if char == "}" and not in_str:
                curly_brackets_count -= 1
            if char == "," and not in_str and square_brackets_count == 0 and curly_brackets_count == 0:
                elems.append(elem)
                elem = ''
            else:
                elem += char
        elems.append(elem)
        elems = map(lambda x: process_assignment_expression(x, functions, functions_lambdas), elems)
        return list(elems)
    elif expression[0] == "{":
        # (possibly nested) dict
        elems_string = expression[1:-1]
        keys = []
        values = []
        elem = ''
        in_str = False

        square_brackets_count = 0
        curly_brackets_count = 0

        for char in elems_string:
            if char == '"':
                in_str = not in_str
            if char == "[" and not in_str:
                square_brackets_count += 1
            if char == "]" and not in_str:
                square_brackets_count -= 1
            if char == "{" and not in_str:
                curly_brackets_count += 1
            if char == "}" and not in_str:
                curly_brackets_count -= 1
            if char == ":" and not in_str and square_brackets_count == 0 and curly_brackets_count == 0:
                keys.append(elem)
                elem = ''
            elif char == "," and not in_str and square_brackets_count == 0 and curly_brackets_count == 0:
                values.append(elem)
                elem = ''
            else:
                elem += char
        values.append(elem)
        keys = map(lambda x: process_assignment_expression(x, functions, functions_lambdas), keys)
        values = map(lambda x: process_assignment_expression(x, functions, functions_lambdas), values)
        return dict(zip(keys, values))
    elif expression[0:2] == "re":
        # Example: re "g/([0-9]+) ([0-9]+)/\\1 + \\2/"" "1 2" 
        # -> "1 + 2"
        print("Expression: ", expression)
        slash_indices = [i for i, c in enumerate(expression) if c == "/"]
        print("Reg: ", expression[5:slash_indices[1]])
        reg = regex.compile(expression[5:slash_indices[1]], regex.VERSION1)  # g/([0-9]+) ([0-9]+)/
        repl = expression[slash_indices[1] + 1:slash_indices[2]]  # (\\1 + \\2)
        print("Repl: ", repl)
        string = expression[expression.rindex("/") + 2:] # "1 2"
        string = string[string.index('"') + 1:string.rindex('"')]
        print("String: ", string)
        result = '"' + reg.sub(repl, string, timeout=1) + '"'
        print("Result: ", result)
        return result
    else:
        return expression_eval(parse(expression), functions, functions_lambdas)

def execute_command(
        command: str, 
        variables: Dict[str, str], 
        message, functions, 
        functions_lambdas,
        global_variables: Dict[str, str],
        user_variables: Dict[str, str],
        ) -> None:
    print(f"Execute command input: {command[:100]}")
    command = substitute_variables(command, variables, message, global_variables, user_variables)
    command = command.replace('return', 'return=')
    if '=' in command:
        assignment = process_assignment_expression(command[command.index("=") + 1:], functions, functions_lambdas)

        global_variable = False
        user_variable = False
        if command[:command.index("=")].startswith("global"):
            global_variable = True
            command = command[6:]
        elif command[:command.index("=")].startswith("user"):
            user_variable = True
            command = command[4:]
        

        if assignment in functions:
            functions.append(command[:command.index("=")])
            functions_lambdas[command[:command.index("=")]] = lambda a: functions_lambdas[assignment](a)
        if type(assignment) == list:
            functions.append(command[:command.index("=")])
            functions_lambdas[command[:command.index("=")]] = lambda a: assignment[a]
        elif type(assignment) == dict:
            functions.append(command[:command.index("=")])
            def f(a: str):
                # if type(a) == str and a[0] == '"':
                #     a = a[1:-1]
                return assignment[a]
            functions_lambdas[command[:command.index("=")]] = f
        else:
            if global_variable:
                global_variables[command[:command.index("=")]] = assignment
            elif user_variable:
                user_variables[command[:command.index("=")]] = assignment
            else:
                variables[command[:command.index("=")]] = assignment
    else:
        return

#program_code = \
#"""
#s = [1, 2, "3"];
#
#a = s(2);
#b = 3 + s(0 + 1);
#
#return "a = $a$, b = $b$";
#"""

#variables = {
#    'name': 'Andrey',
#}

#print(execute_program(program_code, variables, None))

"""
day = ($message.date$ - 1693774800) | 86400; 
week_num = $day$ | 7;
rwn = $week_num$ + 1;
odd = $week_num$ % 2 == 0;
if($odd$) {week = "Нечётная неделя ($rwn$)";} else {week = "Чётная неделя ($rwn$)";}

wday = $day$ % 7 + 1; h = (($message.date$ - 1693774800) % 86400) | 3600 ; m = (($message.date$ - 1693774800) % 3600) | 60;

pp = "Технологии создания ПП"; met = "Численные методы"; anal = "Интеллектуальный анализ данных"; netw = "Компьютерные сети"; s = "Социология"; ops = "Мат.методы исследования операций"; web = "ВЕБ"; mp = "МП и ИУС"; vib = "Вибіркова дисципліна/Нет пары"; fiz = "Физра";
z = "https://us04web.zoom.us/j/";
t = "https://teams.microsoft.com/l/";
me = "https://meet.google.com/";
ppl = "$z$87647753497?pwd=eTJzOGo5bGZnNC9NMGRBVFNKRVlQUT09"; metl = "$t$meetup-join/19:meeting_ZmJlNjg0YzYtMWYwNi00NWU4LWE0N2UtMTg1ZGM1ZGYwYmVl@thread.v2/0?context=%7B%22Tid%22:%22bd2fa240-71fc-45bd-abce-f1bc80beeb0a%22,%22Oid%22:%226e50c4db-d1c1-4aee-989d-96271729c62c%22%7D"; anall = "$t$team/19%3ASgb-mqHnxV7VeamhpvAIXt8QG7MBPmcBvkeJobhJIjs1%40thread.tacv2/conversations?groupId=906eec79-334e-4f26-aa68-b5f95883d2d3&tenantId=bd2fa240-71fc-45bd-abce-f1bc80beeb0a"; netwl = "$z$2265739917?pwd=cGVCa1JZZm9idnFhWEhDYTZZU1daZz09"; sl = "$me$nte-kopn-dzm"; opsl = "$z$4209706766?pwd=YVhZSHVYWGJOVkZLc2t0VFlkbDdxQT09"; mpl = "$me$jrf-dbjh-gab"; webl = "$m$xmg-gjza-bdj"; webl2 = "$me$ixh-ufpj-bwv";
lec = " (лекция)"; pr = " (практика)"; lab = " (лаба)"; no = "Нет пары";

beg = "Пары ещё не начались"; end = "Сегодня пары закончились"; nomore = "Больше сегодня пар нет"; break = "Перерыв";
ts = ["8:00 - 9:35", "9:50 - 11:25", "11:40 - 13:15", "13:30 - 15:05"];

day_names = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"];
day_name = day_names($wday$);

if($wday$ == 6)
{if($week_num$ + 3 > 2) {
wday = ($week_num$ + 3 - 3) % 5 + 1;
odd = $wday$ < 6;
sat = True;
} else {}} else {
sat = False;}

if ($h$ > 15 or ($h$ == 15 and $m$ > 5)) {wd = ($wday$ + 1) % 7;} else {wd = $wday$;}

if ($wd$ == 1){
ps = ["$pp$$lec$", "$web$$lec$", "$mp$$lec$", "$no$"];
ls = ["$ppl$", "$webl$", "$mpl$", ""];
} else {
if ($wd$ == 2){
ps = ["$ops$$lec$", "$met$$lec$", "$anal$$lab$", "$no$"];
ls = ["$opsl$", "$metl$", "$anall$", ""];
} else {
if ($wd$ == 3 and $oddity$){
ps = ["$no$", "$met$$lab$", "$pp$$lab$", "$no$"];
ls = ["", "$metl$", "$ppl$", ""];
} else {
if ($wd$ == 3){
ps = ["$no$", "$mpl$", "$pp$$lab$", "$no$"];
ls = ["", "$mpl$", "$ppl$", ""];
} else {
if ($wd$ == 4 and $odd$){
ps = ["$s$$lec$", "$anal$$lec$", "$netw$$lec$", "$netw$$lab$"];
ls = ["$sl$", "$anall$", "$netwl$", "$netwl$"];
} else {
if ($wd$ == 4){
ps = ["$s$$pr$", "$anal$$lec$", "$netw$$lec$", "$no$"];
ls = ["$sl$", "$anall$", "$netwl$", ""];
} else {
if ($wd$ == 5){
ps = ["$vib$", "$web$$lab$", "$ops$$lab$", "$fiz$"];
ls = ["", "$webl2$", "$opsl$", ""];
} else {
ps = ["$no$", "$no$", "$no$", "$no$"];
ls = ["", "", "", ""];
}}}}}}}

time = "";
pair = "";
link = "";
next_pair = "";
next_link = "";
next_time = "";

pno = 8;
pne = 8;

if($h$<8) {
pair = "$beg$";
pne = 0;
} else {
if($h$<9 or ($h$==9 and $m$<35)) {
pno = 0;
pne = 1;
} else {
if($h$<9 or ($h$==9 and $m$<50)) {
pair = "$break$";
pne = 1;
} else {
if($h$<11 or ($h$==11 and $m$<25)) {
pno = 1;
pne = 2;
} else {
if($h$<11 or ($h$==11 and $m$<40)) {
pair = "$break$";
pne = 2;
} else {
if($h$<13 or ($h$==13 and $m$<15)) {
pno = 2;
pne = 3;
} else {
if($h$<13 or ($h$==13 and $m$<30)) {
pne = 3;
} else {
if($h$<15 or ($h$==15 and $m$<05)) {
pno = 3;
next_pair = "$nomore$";
} else {
pair = "$end$";
pne = 0;
}}}}}}}}

if($pno$ != 8) {
pair = ps($pno$);
link = ls($pno$);
time = ts($pno$);
} else {}

if($pne$ != 8) {
next_pair = ps($pne$);
next_link = ls($pne$);
next_time = ts($pne$);
} else {}


if($sat$ == False) {
tom = "Следующая пара: 
$next_time$ <a href='$next_link$'>$next_pair$</a>";}
else{tom = "";}

return "Сейчас $week$, $day_name$, $h$ часа $m$ минут.

Текущая пара:
$time$ <a href='$link$'>$pair$</a>

$tom$";
"""