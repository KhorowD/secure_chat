import pprint
import yaml 

class ClientContext():
    """
    Структура содержащая информацию о подключаемых клиентах
    """
    def __init__(self) -> None:
        self.username = ""
        self.password = ""
        self.isRegistered = False #Если пользователь залогинился, тогда ставим True
        self.isRegisteredRemote = False #Если пользователь прошел регистрацию устройства, ставим True
        # self.nonce = ""
        self.nonce_128 = ""
        # self.nonce_new = ""
        self.nonce_256 = ""
        self.pq = ""
        self.p = ""
        self.q = ""
        self.server_nonce = ""
        self.server_rsa_priv_key = ""
        self.server_rsa_n_value = ""
        self.dh_pub_key = ""
        self.dh_priv_key = ""
        self.dh_g = ""
        self.dh_p = ""
        self.dh_server_pub_key = ""
        self.dh_server_priv_key = ""
        self.auth_key_hash = ""
        self.auth_key = ""
        self.chats = {}
        self.e2e_requests = []
        self.e2e_accepted_requests = {}
        self.e2e_passed_parameters = {}
        self.e2e_g = ""
        self.e2e_p = ""
        self.e2e_dh_pub_key = ""
        self.tgt_user = ""
        self.key_1 = ""
        self.key_2 = ""
        self.server_pub_key_fingerprint = ""
        
        
    def read_config(self, file_path):
        """
        Чтения конфигурации клиента из yaml файла
        """
        with open(file_path, "r") as file:
                # config = yaml.load(file, Loader=SafeLoader).get("ping_script", {})
            session = yaml.safe_load(file)
            print("Loaded user session\n", session, "\n"+"+"*25)


        return session

    def save_user_config(client_data : dict):
        """
        Записываем текущие параметры клиента в yaml файл
        """
        # with open("./sessions/user_config.txt", "w") as conf:
        #         pprint(self.client_data.__dict__, conf)

        document = {
            "user":
            {
                "name": None,
                "session" : None, 
                "pass_md5_hash": None,
                "local_registration": None,
                "remote_registration": None
            },
            "crypto": 
            {
                "nonce_128" : None,
                "nonce_256" : None, 
                "auth_key": None,
                "auth_key_hash": None,
                "dh": 
                {
                    "p": None,
                    "g": None,
                    "priv_key": None,
                    "pub_key": None
                }
            },
            "pow": 
            {
                "pq": None
                "p": None
                "q": None
            },
            "server_data":
            {
                "pub_key_fingerprint": None
            }
        }



        with open(self.client_data.username+"_session.yml", "w") as conf:
            try:
                yaml.dump(self.client_data.__dict__, conf)
            except Exception as e:
                print(e)
                message_box("Сессия клиента не сохранена!", "Error!",
                        QtWidgets.QMessageBox.Critical,
                        QtWidgets.QMessageBox.Ok)
                return None

    def __print__(self):
        pprint.pprint(self.__dict__)