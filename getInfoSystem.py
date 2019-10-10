# coding: utf-8

import socket, subprocess, platform, win32com.client, os, shutil, wmi, ctypes
from psutil import virtual_memory
from hwinfo.pci import PCIDevice
from hwinfo.pci.lspci import LspciNNMMParser
from subprocess import check_output

CONST_SENHA_PADRAO = "mudar@adM123"

# check if is admin console
def is_Admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def getBasicInfoSystem():
    hostname = socket.gethostname()
    windows = platform.platform()
    basic = [hostname, windows]
    return basic

def get_cpu_type():
    from win32com.client import GetObject
    root_winmgmts = GetObject("winmgmts:root\cimv2")
    cpus = root_winmgmts.ExecQuery("Select * from Win32_Processor")
    return cpus[0].Name

def get_total_memory():
	mem = virtual_memory()
	memory = mem.total / 1024.**3
	return "MEM: "+str(round(float(memory)))

def get_total_hd():
	total, used, free = shutil.disk_usage("/")
	return "HD: %d GB" % (total // (2**30))

def getBrandAndModel(arg):
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_BIOS")
    for objItem in colItems:
        if objItem.SerialNumber != None:
            SERVICE_TAG = str(objItem.SerialNumber)
        if objItem.Version != None:
            MARCA = str(objItem.Version)
            string = MARCA.split(" ")
    return string[0]+" "+arg+" "+SERVICE_TAG

def run_command_cmd():
	serial = str(subprocess.run('wmic path softwarelicensingservice get OA3xOriginalProductKey', stdout=subprocess.PIPE))
	return serial

def generateInfo():
    c = wmi.WMI()
    systeminfo = c.Win32_ComputerSystem()[0]

    Manufacturer = systeminfo.Manufacturer
    Model = systeminfo.Model

    f = open(str(socket.gethostname())+".txt", "w+")
    f.write("HOSTNAME: "+getBasicInfoSystem()[0]+"\n")
    f.write(get_total_memory()+"GB"+"\n")
    f.write(get_total_hd()+"\n")
    f.write(get_cpu_type()+"\n")
    f.write(getBrandAndModel(Model)+"\n")
    f.write(getBasicInfoSystem()[1]+"\n\n")
    f.write(run_command_cmd()+"\n")
    f.close()

# check console open with admin privileges
if is_Admin():
    decision = input("Deseja renomear computador? y/n ")
    if decision == 'n':
        print("\n")
    elif decision == 'y':
        nameComputer = input('Digite o nome do computador: ')
        subprocess.call(['powershell.exe', "Rename-Computer -NewName "+nameComputer])
    else:
        print('Opção inválida!')

    print("Ativando usuario Administrador")
    subprocess.call(['powershell.exe', "net user Administrador /active:yes"])
    print("Alterando senha do usuario Administrador!")
    subprocess.call(['powershell.exe', "net user Administrador "+ CONST_SENHA_PADRAO])
    print('Gerando .txt com informações do computador!')
    generateInfo()
    print('.txt gerado com sucesso!')
else:
    print('Não foi possivel executar o script. Execute - o como administrador!')

