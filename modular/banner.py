from colorama import Fore, Style, Back, init
import random

init(autoreset=True)

versi = "2.0"
author = "CayberMods"

COLORS = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, 
    Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTRED_EX,
    Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX
]

def random_color():
    return random.choice(COLORS)

def get_banner():
    c1 = random_color()
    c2 = random_color()
    c3 = random_color()
    c4 = random_color()
    c5 = random_color()
    c6 = random_color()
    c7 = random_color()
    
    text_color = random_color()
    
    version_text = f"{Style.BRIGHT}{text_color} Version: {versi} - {author} {Style.RESET_ALL}"
    
    banner = f"""
{Style.BRIGHT}{c1} $$$$$$\\                      $$\\      $$\\                 $$\\
{c2} $$  __$$\\                     $$$\\    $$$ |                $$ |
{c3} $$ /  \\__| $$$$$$\\   $$$$$$$\\ $$$$\\  $$$$ | $$$$$$\\   $$$$$$$ |
{c4} \\$$$$$$\\  $$  __$$\\ $$  _____|$$\\$$\\$$ $$ |$$  __$$\\ $$  __$$ |
{c5}  \\____$$\\ $$ /  $$ |$$ /      $$ \\$$$  $$ |$$$$$$$$ |$$ /  $$ |
{c6} $$\\   $$ |$$ |  $$ |$$ |      $$ |\\$  /$$ |$$   ____|$$ |  $$ |
{c7} \\$$$$$$  |\\$$$$$$  |\\$$$$$$$\\ $$ | \\_/ $$ |\\$$$$$$$\\ \\$$$$$$$ |
{c1}  \\______/  \\______/  \\_______|\\__|     \\__| \\_______| \\_______|
{Style.RESET_ALL}
{Back.BLACK}{Style.BRIGHT}{random_color()}                                      {version_text}{Style.RESET_ALL}
"""
    return banner

def print_banner():
    print(get_banner())