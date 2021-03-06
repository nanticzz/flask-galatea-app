#This file is part galatea app for Flask.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from flask import current_app, session
from galatea.tryton import tryton

@current_app.context_processor
def cms_processor():

    def menu(code=None, levels=9999):
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

        login = session.get('logged_in')
        manager = session.get('manager')

        # Search by code
        menus = Menu.search([
            ('code', '=', code),
            ], limit=1)
        if not menus:
            return []
        menu, = menus

        def get_menus(menu, levels, level=0):
            childs = []
            if level < levels:
                level += 1
                for m in menu.childs:
                    if m.login and not login:
                        continue
                    if m.manager and not manager:
                        continue
                    childs.append(get_menus(m, levels, level))
            return {
                'id': menu.id,
                'name': menu.name,
                'slug': menu.slug,
                'childs': childs,
                'nofollow': menu.nofollow,
                'icon': menu.icon,
                'css': menu.css,
                }

        menu = get_menus(menu, levels)
        return menu['childs']

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

    def carousel(code=None):
        """
        Return object values carousel by code
        
        HTML usage in template:

        {% from "_helpers.html" import render_carousel %}
        {% set carousel=cms_carousel('test') %}{{ render_carousel(carousel) }}
        """
        if not code:
            return None

        Carousel = tryton.pool.get('galatea.cms.carousel')

        # Search by code
        carousels = Carousel.search([('code', '=', code)])
        if not carousels:
            return None
        carousel, = carousels
        return carousel

    def catalog_menu(slug=None, levels=9999):
        """
        Return object values catalog menu by slug
        
        HTML usage in template:

        {% set menus=catalog_menu('slug') %}
        {% if menus %}
            {% for menu in menus %}
                <a href="{{ menu.slug }}" alt="{{ menu.name }}">{{ menu.name }}</a>
            {% endfor %}
        {% endif %}
        """
        if not slug:
            return []

        Menu = tryton.pool.get('esale.catalog.menu')

        # Search by code
        menus = Menu.search([
            ('slug', '=', slug),
            ('website', '=', GALATEA_WEBSITE),
            ], limit=1)
        if not menus:
            return []
        menu, = menus

        def get_menus(menu, levels, level=0):
            childs = []
            if level < levels:
                level += 1
                for m in menu.childs:
                    childs.append(get_menus(m, levels, level))
            return {
                'id': menu.id,
                'name': menu.name,
                'slug': menu.slug,
                'childs': childs,
                }

        menu = get_menus(menu, levels)
        return menu['childs']

    return dict(
        cms_menu=menu,
        cms_block=block,
        cms_carousel=carousel,
        catalog_menu=catalog_menu,
        )
