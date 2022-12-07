import ldap3, time

class AD:
    def __init__(self, username, password, domain, dc_list, host_port, LDAP_Subtree, reqLDAPattr, LDAP_SearchFilter):
        self.LDAP_SearchFilter = LDAP_SearchFilter
        self.reqLDAPattr = reqLDAPattr
        self.LDAP_Subtree = LDAP_Subtree
        self.host_port = host_port
        self.dc_list = dc_list
        self.domain = domain
        self.password = password
        self.username = username

    def get_realtimestat(self):
        result = []
        server_pool = ldap3.ServerPool(None, ldap3.ROUND_ROBIN, active=1)
        for dc in self.dc_list:
            server_pool.add(ldap3.Server(dc,get_info=ldap3.ALL, port=self.host_port))
            try:
                conn = ldap3.Connection(server=server_pool,
                                        user=self.username,
                                        password=self.password,
                                        authentication=ldap3.NTLM,
                                        read_only=True)
                conn.bind()
                entry_generator = conn.extend.standard.paged_search(search_base=self.LDAP_Subtree,
                                                                    search_filter=self.LDAP_SearchFilter,
                                                                    attributes=self.reqLDAPattr,
                                                                    paged_size=5,
                                                                    generator=True)
                for entrygen in entry_generator:
                    tuz = entrygen['attributes']
                    if len(tuz.get('lockoutTime')) == 0:
                        tuz['lockoutTime'] = 0
                    attribute_dict = {
                        'AcountName': tuz.get('userPrinipalName'),
                        'TUZ_AccountControl': tuz.get('userAccountControl'),
                        'TUZ_lockoutTime': tuz.get('lockoutTime'),
                        'TUZ_pwdLastSet': time.mktime(tuz.get('pwdLastSet').timetuple()),
                        'TUZ_description': tuz.get('description')
                    }
                    result.append(attribute_dict)
            finally:
                conn.unbind()
                conn.closed
            return result
