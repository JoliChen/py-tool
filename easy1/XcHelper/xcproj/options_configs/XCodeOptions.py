# -*- coding: UTF-8 -*-

from XcHelper.xcproj.biplist import writePlist

# 出包方式
class JExportOptions:
    APPSTORE = 'app-store'
    DEVELOPMENT = 'development'

# 出包配置
class JOptionsPlist:
    def __init__(self):
        self.options = None

    def reset(self, opt_method):
        if opt_method  == JExportOptions.APPSTORE:
            self.options = {
                'provisioningProfiles': {
                    '%product_identifier%': '%provisioning_profile_specifier%'
                },
                'teamID': '%development_team%',
                'stripSwiftSymbols': True,
                'signingCertificate': 'iPhone Distribution',
                'uploadSymbols': False,
                'signingStyle': 'manual',
                'method': 'app-store',
                'uploadBitcode': False
            }
        elif opt_method == JExportOptions.DEVELOPMENT:
            self.options = {
                'compileBitcode': False,
                'provisioningProfiles': {
                    '%product_identifier%': '%provisioning_profile_specifier%'
                },
                'teamID': '%development_team%',
                'thinning': '<none>',
                'stripSwiftSymbols': True,
                'signingCertificate': 'iPhone Developer',
                'signingStyle': 'manual',
                'method': 'development'
            }
        # print 'default options:%s' % self.options

    def set_sign(self, identifier, team_id, specifier):
        assert self.options is not None, 'options is None'
        self.options['provisioningProfiles'] = {identifier: specifier}
        self.options['teamID'] = team_id

    def write_to_file(self, path):
        is_ok = writePlist(self.options, path, False)
        assert not is_ok, 'save options error'