# -*- coding: UTF-8 -*-

class iOSHIG:
    ICON_APP = 'App'
    ICON_SPOTLIGHT = 'Spotlight'
    ICON_SETTING = 'Settings'
    ICON_NOTIFICATION = 'Notification'

    ICON_RATE = {
        ICON_APP: 100, ICON_SPOTLIGHT: 20, ICON_SETTING: 20, ICON_NOTIFICATION: 20
    }

    ICON_SIZE = {
        ICON_APP: {
            'iPhone': ['60@3x', '60@2x'],
            'iPad Pro': ['83.5@2x'],
            'iPad, iPad mini': ['76@1x', '76@2x'],
            'App Store': ['1024@1x']
        },
        ICON_SPOTLIGHT: {
            'iPhone': ['40@3x', '40@2x'],
            'iPad Pro, iPad, iPad mini': ['40@2x']
        },
        ICON_SETTING: {
            'iPhone': ['29@3x', '29@2x'],
            'iPad Pro, iPad, iPad mini': ['29@2x']
        },
        ICON_NOTIFICATION: {
            'iPhone': ['20@3x', '20@2x'],
            'iPad Pro, iPad, iPad mini': ['20@2x']
        }
    }

    LAUNCH_SCREEN = {
        'iPhone SE': '640×1136',
        'iPhone 6s': '750×1334',
        'iPhone 6s Plus': '1242×2208',
        'iPhone 7': '750×1334',
        'iPhone 7 Plus': '1242×2208',
        'iPhone 8': '750×1334',
        'iPhone 8 Plus': '1242×2208',
        'iPhone X': '1125×2436',
        '7.9 iPad mini 4': '1536×2048',
        '9.7 iPad': '1536×2048',
        '10.5 iPad Pro': '1668×2224',
        '12.9 iPad Pro': '2048×2732'
    }