from pipython import GCSDevice


class NIController:
    def __init__(self):
        super(NIController, self).__init__()
        with GCSDevice('C-867') as self.device:
            self.device.ConnectRS232(comport=4, baudrate=9600)

            if GCSDevice.IsRunningMacro(self.device):
                startup_macro = GCSDevice.qRMC(self.device).strip('\n')
                print(type(startup_macro))
                print(startup_macro)
                print(f'Currently running macro: {startup_macro}, closing...')
                GCSDevice.MAC_STOP(self.device, [1])
            else:
                print(f'Not running any macros on startup')

    def testing(self):
        self.device.InterfaceSetupDlg(key='sample')
        print('connected: {}'.format(self.device.qIDN().strip()))
        if self.device.HasqVER():
            print('version info: {}'.format(self.device.qVER().strip()))
        GCSDevice.MAC_START(self.device, macro='TEST')


control = NIController()