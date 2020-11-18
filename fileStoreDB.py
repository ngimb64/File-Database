import sqlite3, base64, sys, os, socket, smtplib, requests, pathlib, cv2, re
from pyfiglet import Figlet
from hashlib import sha512
from cryptography.fernet import Fernet
from time import sleep
from platform import platform
from email import message_from_string
from termcolor import colored

def email():
    os_ver = platform() ; host = socket.gethostname()
    ip = socket.gethostbyname(host) ; user = os.getlogin()
    try:
        public_ip = requests.get('https://api.ipify.org').text

    except requests.ConnectionError:
        public_ip = '* Public Ip Address not available *'    

    text = '''
          * Database max login attempts detected *
          --------------------------------------------------------------------
           Os Name:     {}
           Hostname:    {}
           Public IP:   {}
           Private IP:  {}
           Username:    {}
           '''.format(os_ver, host, public_ip, ip, user)

    msg = message_from_string(text)
    email_addr = ''                 # <= Enter email address
    password = ''                   # <= Enter email password
    msg['Subject'] = 'Admin Alert'

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email_addr, password)
        s.sendmail(email_addr, email_addr, msg.as_string())

    except:
        os.system('cls')
        print('* Error Occured *')
        sleep(2)
        os.exit(1)

    return

def main():
    pathlib.Path('./Dock').mkdir(parents=True, exist_ok=True)
    count = 0
    while True:
        os.system('cls')
        if count == 3:
            print('Excessive authentication attempts detected .. 5 minute timeout')
            email()
            sleep(300)
            continue

        if len(sys.argv) == 1:
            prompt = input('Enter password:\n')
        else:
            prompt = sys.argv[1]

        usrInput = sha512(prompt.encode()).hexdigest()
        k = b'rIrnf6II663snpuje0gO4U6ueJ5zHzTojaMuaVM9XgI='
        scrt = b'gAAAAABfoJG4ChmatZdzBrfMNBVwyYuHcU3gO48WemSkB1WnwI0Hchawjmp4FQmbdD9_prttCn4luKcU2RZhT0xzbVY0FYCyBbab_3PtBiGTwMj034-KnyHdvRnMKhap2yFFkWTWIwNsqnGC4KMwc-MyjV_0QQUYYdDENnUjkjklUhfRF-oNrnzMaR8UEo6Upl8jYYnQas7GJnFVpQfFwsKqtxWSnyatN7CeeVrU1JkcdpjsfjlSMI4DwItQ7z4rP3lD9dSTLEkY'
        dec = Fernet(k).decrypt(scrt)

        if usrInput == dec.decode():
            print('Authentication Successful!')
            sleep(1)
            break

        print('\n* Password attempt incorrect *')
        sleep(0.75)
        count += 1

    try:
        conn = sqlite3.connect('storageDB.db')
        conn.execute('''
                     CREATE TABLE storage(
                     full_name TEXT PRIMARY KEY NOT NULL,
                     name TEXT NOT NULL,
                     extension TEXT NOT NULL,
                     files TEXT NOT NULL);
                     ''')
        print('\nStorage database created')

    except:
        print('\n* Database already exists .. *')

    sleep(1.5)
    custom_fig = Figlet(font='roman' , width=130)

    while True:
        os.system('cls')
        print(custom_fig.renderText('$ File Server $'))
        print('''
        #--------------------------#
        |        {}         |
        #==========================#
        |    l => List Contents    |
        |    o => Open File        |
        |    s => Store File       |
        |    e => Exit Database    |
        #--------------------------#
        '''.format(colored('Commands:', 'red')))

        prompt = input('#>>: ')

        # List Database Contents #
        if prompt == 'l':
            query = conn.execute('SELECT * FROM storage;')
            rows = query.fetchall()
            print('\nFiles Available:\n-=-=-=-=-=-=-=-=-=-')
            [ print('{} => {}'.format(index, row[0])) for index,row in enumerate(rows) ]
            sleep(4)
            continue

        # Open File #
        elif prompt == 'o':
            file_name = input('File name or number?\n')
            file_type = input('\nFile type?\n')
            try:
                if file_name.isdigit() == True:
                    query = conn.execute('SELECT * FROM storage;')
                    rows = query.fetchall()
                    files = []
                    for row in rows:
                        files.append(row[0])

                    query = conn.execute('SELECT * FROM storage WHERE full_name=\"{}\";'\
                                         .format(files[int(file_name)]))
                    file_string = b''
                    for row in query:
                        file_string = '{}'.format(row[3])
                        break

                    re_fix = re.compile(r'(?:^b\'|\'$)', re.MULTILINE)
                    file_string = re.sub(re_fix, r'', file_string)
                    decodedBytes = base64.b64decode(file_string)
                    try:
                        with open('./Dock/' + files[int(file_name)], 'ab') as fileIO:
                            fileIO.write(decodedBytes)
                            print('\nFile available in program directory')
                            sleep(1.5)

                    except IOError as err:
                        print('\n* File Error: {} *\nFile could already exist ..'.format(err))
                        sleep(4)
                        continue

                    continue

                else: 
                    query = conn.execute('SELECT * FROM storage WHERE full_name=\"{}.{}\";'\
                            .format(file_name, file_type))

            except sqlite3.OperationalError as err:
                print('\n* Operational Error: {} *\nFile storage failed..'.format(err))
                sleep(4)
                continue

            except sqlite3.IntegrityError as err:
                print('\n* Integrity Error: {} *\nFile storage failed..'.format(err))
                sleep(4)
                continue

            file_string = b''
            for row in query:
                file_string = row[3]

                break

            re_strip = re.compile(r'(?:^b\'|\'$)', re.MULTILINE)
            try:
                file_string = re.sub(re_strip, r'', file_string)

            except TypeError:
                print('* Improper data format entered *')
                sleep(2)
                continue

            try:
                with open('./Dock/' + file_name + '.' + file_type, 'wb') as fileIO:
                    decodedBytes = base64.b64decode(file_string)
                    fileIO.write(decodedBytes)
                    print('\nFile available in program directory')
                    sleep(1.5)

            except IOError as err:
                print('\n* File Error: {} *\nFile could already exist ..'.format(err))
                sleep(4)

            continue

        # Store File #
        elif prompt == 's':
            path = input('Enter the absolute path of item to store or '\
                         'hit enter to store files from the Dock directory:\n')
            re_check = re.compile(r'/.+\.(?:txt|py|html|jpg|png|jpeg)$')
            name, ext = [], []

            if path == '':
                file_name = os.getcwd() + '\\Dock'
                for dirpath, dirnames, filenames in os.walk(file_name):
                    for file in filenames:
                        res = file.split('.')
                        name.append(res[0]) ; ext.append(res[1])

            elif re_check.search(path):
                file_name = path.split('/')
                file_name = file_name[len(file_name) - 1]
                res = file_name.split('.')
                name.append(res[0]) ; ext.append(res[1])

            else:
                print('* File path incorrect *')
                sleep(2)
                continue

            extensions =  {
                'txt': 'TEXT',
                'py': 'TEXT',
                'html': 'TEXT',
                'jpg': 'IMAGE',
                'png': 'IMAGE',
                'jpeg': 'IMAGE'
            }

            re_path = re.compile(r'\./.+\.(?:txt|py|html|jpg|jpeg|png)$')

            for n,e in zip(name,ext): 
                try:
                    ext_type = extensions[e]

                except:
                    print('* Improper file extension format *')
                    sleep(4)
                    continue

                file_string = b''
                if path == '':
                    path = './Dock/{}.{}'.format(n, e)

                if ext_type == 'IMAGE':
                    img = cv2.imread(path)
                    file_string = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()

                elif ext_type == 'TEXT':
                    with open(path, 'rb') as file_string:
                        file_string = base64.b64encode(file_string.read())

                if re_path.match(path):
                    file_name = path.split('/')[-1]

                command = 'INSERT INTO storage (full_name, name, extension, files)'\
                          'VALUES (\"{}\",\"{}\",\"{}\",\"{}\");'\
                          .format(file_name, n, ext_type, file_string)
                try:
                    conn.execute(command)
                    conn.commit()

                except sqlite3.OperationalError as err:
                    print('* Operational Error: {} *\nFile storage failed..'.format(err))
                    sleep(4)
                    continue

                except sqlite3.IntegrityError as err:
                    print('* Integrity Error: {} *\nFile storage failed..'.format(err))
                    sleep(4)
                    continue


                path = ''
                print('$ File {} Stored $\n'.format(file_name))
                os.remove('./Dock/{}'.format(file_name))
                sleep(1.5)

            print('All files in Dock have been stored')
            sleep(2)
            continue

        elif prompt == 'e':
            print('\nExiting Database ..')
            sleep(0.75)
            break

        print('\n* Improper Input *')
        sleep(0.75)

    return

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('\n* Ctrl + C detected .. exiting *')