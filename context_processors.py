#This file is part galatea app for Flask.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from flask import current_app, session
from galatea.tryton import tryton

@current_app.context_processor
def cms_processor():

    def menu(code=None):
        """
        Return object values menu by code
        
        HTML usage in template:

        {% set menus=cms_menu('code') %}
        {% if menus %}
            {% for menu in menus %}
                <a href="{{ menu.slug }}" alt="{{ menu.name }}">{{ menu.name }}</a>
            {% endfor %}
        {% endif %}
        """
        if not code:
            return []

        Menu = tryton.pool.get('galatea.cms.menu')

        # Search by code
        menus = Menu.search([('code', '=', code)])
        if not menus:
            return []
        menu, = menus

        def get_menus(menu):

            childs = []
            for m in menu.childs:
                childs.append(get_menus(m))
            return {'name': menu.name, 'slug': menu.slug, 'childs': childs}
        menu = get_menus(menu)

        return menu['childs']

    def block(code=None):
        """
        Return the HTML content

        HTML usage in template:

        {% set image=cms_block('code') %}{{ image|safe }}
        {% set remote_image=cms_block('code') %}{{ remote_image|safe }}
        {% set custom_code=cms_block('code') %}{{ custom_code|safe }}
        """
        if not code:
            return ''

        StaticFile =tryton.pool.get('galatea.static.file')
        Block = tryton.pool.get('galatea.cms.block')

        # Search by code
        fields_names = ['type', 'click_url', 'file',
            'remote_image_url', 'custom_code', 'height', 'width',
            'alternative_text', 'click_url']
        blocks = Block.search_read([('code', '=', code)], limit=1, fields_names=fields_names)
        if not blocks:
            return ''
        block, = blocks

        if block['type'] == 'image':
            file = StaticFile(block['file'])
            block['file'] = file.url

            if not block.get('alternative_text'):
                block['alternative_text'] = ''
            if not block.get('width'):
                block['width'] = ''
            if not block.get('height'):
                block['height'] = ''

            image = u'<img src="%(file)s" alt="%(alternative_text)s"' \
                    u' width="%(width)s" height="%(height)s"/>' % {
                        'file': block['file'],
                        'alternative_text': block['alternative_text'],
                        'width': block['width'],
                        'height': block['height'],
                        }
            if block.get('click_url'):
                image = u'<a href="%(click_url)s">%(image)s</a>' % {
                        'click_url': block['click_url'],
                        'image': image,
                        }
            return image

        elif block['type'] == 'remote_image':
            if not block.get('alternative_text'):
                block['alternative_text'] = ''
            if not block.get('width'):
                block['width'] = ''
            if not block.get('height'):
                block['height'] = ''

            image = u'<img src="%(remote_image_url)s" alt="%(alternative_text)s"' \
                    u' width="%(width)s" height="%(height)s"/>' % {
                        'remote_image_url': block['remote_image_url'],
                        'alternative_text': block['alternative_text'],
                        'width': block['width'],
                        'height': block['height'],
                        }
            if block.get('click_url'):
                image = u'<a href="%(click_url)s">%(image)s</a>' % {
                        'click_url': block['click_url'],
                        'image': image,
                        }
            return image

        elif block['type'] == 'custom_code':
            return block['custom_code']

    def show_price():
        guest_price = current_app.config.get('TRYTON_CATALOG_GUEST_PRICE')
        login_price = current_app.config.get('TRYTON_CATALOG_LOGIN_PRICE')
        manager_price = current_app.config.get('TRYTON_CATALOG_MANAGER_PRICE')

        show_price = False
        # guest users
        if guest_price:
            return True
        # login users
        if not show_price and (login_price and session.get('logged_in')):
            return True
        # manager users
        if not show_price and (manager_price and session.get('manager')):
            return True
        return show_price

    return dict(cms_menu=menu, cms_block=block, show_price=show_price)