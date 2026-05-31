import random

LOGOS = {}

LOGOS["ascii_hammer"] = r"""
{logo}                 ##########       #
{logo}               ##########          ###
{logo}            ##########               ####
{logo}         ###########                  #####
{logo}       ########## #####                ######
{logo}        #####      #####              ######
{logo}          #           #####            #######
{logo}                        #####         #######
{logo}                           #####       #######
{logo}                             #####   ########
{logo}                                #############
{logo}             ##                   ##########
{logo}           #######          ##############
{logo}         ##### #############################
{logo}       #####     ###################     #####
{logo}     #####            #######              #####
{logo}    #####                                      #####
{logo}    ##                                          ##
"""

LOGOS["ussr"] = r"""
{accent}             {c}СССР
{accent}       ________________
{accent}      /                \
{logo}     |   ☭   ССССР   ☭   |
{accent}      \________________/
{accent}      {c}Пролетарии всех стран,
{accent}      {c}соединяйтесь!
"""

LOGOS["soviet_star"] = r"""
{logo}         _____________
{logo}        /             \
{logo}       |   ☆  ☆  ☆   |
{logo}       |   ☆  ☭  ☆   |
{logo}       |   ☆  ☆  ☆   |
{logo}        \_____________/
{accent}   {c}Рабочие мира, объединяйтесь!
"""

LOGOS["cccp_shield"] = r"""
{accent}       ╔═══════════════════╗
{accent}       ║                   ║
{logo}       ║   ☭  C C C P  ☭   ║
{accent}       ║                   ║
{accent}       ╚═══════════════════╝
{accent}   {c}Власть — Советам!
"""

LOGOS["hammer_sickle"] = r"""
{logo}          __
{logo}         / /
{logo}   ____/ /    ___
{logo}  / __  /    / _ \\
{accent} / /_/ /    |  __/
{accent} \____/   {logo}{c}☭{accent}
{accent}  {c}Серп и Молот
"""

LOGOS["red_flag"] = r"""
{accent}  ╔══════════════════════╗
{accent}  ║                      ║
{logo}  ║   ☭  КОММУНИЗМ  ☭   ║
{logo}  ║   ☭    ПОБЕДИТ   ☭   ║
{accent}  ║                      ║
{accent}  ╚══════════════════════╝
{accent}    {c}Вперёд, к победе
{accent}    {c}коммунизма!
"""

LOGOS["prc"] = r"""
{accent}      ╔══════════════════╗
{accent}      ║                  ║
{logo}      ║    ★ 中华人民共和国 ★    ║
{accent}      ║                  ║
{accent}      ╚══════════════════╝
{accent}   {c}全世界无产者，联合起来！
"""

LOGOS["prc_flag"] = r"""
{accent}      ╔══════════════════╗
{logo}      ║  ★  ★  ★  ★  ★  ║
{logo}      ║  ★              ★  ║
{accent}      ║  ★  ★  ★  ★  ★  ║
{accent}      ╚══════════════════╝
{accent}     {c}中华人民共和国万岁
"""

LOGOS["cuba"] = r"""
{accent}    ╔══════════════════════╗
{accent}    ║                      ║
{logo}    ║    ★  ☭  C U B A  ☭  ★    ║
{accent}    ║                      ║
{accent}    ╚══════════════════════╝
{accent}    {c}¡Patria o Muerte!
{accent}       {c}Venceremos!
"""

LOGOS["dprk"] = r"""
{accent}    ╔══════════════════════╗
{accent}    ║                      ║
{logo}    ║    ★  DPRK  ★    ║
{accent}    ║                      ║
{accent}    ╚══════════════════════╝
{accent}     {c}위대한 김일성-김정일주의
"""

LOGOS["vietnam"] = r"""
{accent}    ╔══════════════════════╗
{accent}    ║                      ║
{logo}    ║    ★  VIỆT NAM  ★    ║
{accent}    ║                      ║
{accent}    ╚══════════════════════╝
{accent}   {c}Đảng Cộng sản Việt Nam
{accent}   {c}quang vinh muôn năm!
"""

LOGOS["east_germany"] = r"""
{accent}    ╔══════════════════════╗
{accent}    ║                      ║
{logo}    ║       ☭  DDR  ☭       ║
{logo}    ║   Deutsche Demokratische  ║
{logo}    ║       Republik        ║
{accent}    ║                      ║
{accent}    ╚══════════════════════╝
{accent}   {c}Proletarier aller Länder,
{accent}   {c}vereinigt euch!
"""

LOGOS["laos"] = r"""
{accent}    ╔══════════════════════╗
{accent}    ║                      ║
{logo}    ║    ★  LAO PDR  ★    ║
{accent}    ║                      ║
{accent}    ╚══════════════════════╝
{accent}   {c}ສາທາລະນະລັດ ປະຊາທິປະໄຕ
{accent}   {c}ປະຊາຊົນລາວ
"""

LOGOS["anarcho"] = r"""
{accent}         ╔═══════════╗
{logo}         ║     Ⓐ     ║
{logo}         ║  ☭  Ⓐ  ☭  ║
{accent}         ║           ║
{accent}         ╚═══════════╝
{accent}   {c}No gods, no masters,
{accent}   {c}all free!
"""

LOGOS["simple_commie"] = r"""
{logo}     ☭  COMMIEFETCH  ☭
{accent}   {c}of the people, by the people,
{accent}   {c}for the people
"""

LOGOS["tankie"] = r"""
{accent}      ╔══════════════════╗
{logo}      ║     ☭  T-34  ☭     ║
{logo}      ║   ████████████   ║
{logo}      ║   ████████████   ║
{accent}      ╚══════════════════╝
{accent}   {c}За Родину! За Сталина!
"""

LOGOS["mao"] = r"""
{accent}    ╔══════════════════════╗
{accent}    ║                      ║
{logo}    ║     ★ 毛泽东  ★     ║
{logo}    ║  毛泽东思想万岁   ║
{accent}    ║                      ║
{accent}    ╚══════════════════════╝
{accent}   {c}为人民服务
"""

LOGOS["small_hammer"] = r"""
{logo}      __
{logo}     / /
{logo}  __/ / ___
{logo} / _  / / _ \\
{accent} \__,_/  ___/
{accent}   {c}commiefetch
"""


def get_logo(name="default"):
    if name == "random":
        name = random.choice(list(LOGOS.keys()))
    if name == "default" or name not in LOGOS:
        name = "ascii_hammer"
    return LOGOS.get(name, LOGOS["ascii_hammer"])


def list_logos():
    return list(LOGOS.keys())
