import pprint

class ClientContext():
    """
    Структура содержащая информацию о подключаемых клиентах
    """
    def __init__(self) -> None:
        self.username = ""
        self.nonce = ""
        self.nonce_new = ""
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
        
        
    def read_config():
        """
        Чтения конфигурации клиента из yaml файла
        """
        pass

    def save_user_config():
        """
        Записываем текущие параметры клиента в yaml файл
        """
        pass

    def __print__(self):
        pprint.pprint(self.__dict__)