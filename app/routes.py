import random
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import Skill, Hero, SkillPool, CurrentSkill, Marker, Card, Equipment, GameState, HeroPool, HeroMarkerPool, HeroDetail
import json

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return redirect(url_for('routes.index_local'))

@bp.route('/local')
def index_local():
    hero_id = request.args.get('hero_id')
    hero = None
    current_hero_skills = []
    hero_markers = []
    
    if hero_id:
        hero = Hero.query.get(hero_id)
        if hero:
            current_hero_skills = [{'name': s.name, 'description': s.description, 'type': s.skill_type} for s in hero.skills]
            marker_pool = HeroMarkerPool.query.filter_by(hero_name=hero.name).all()
            for mp in marker_pool:
                marker = Marker.query.filter_by(name=mp.marker_name).first()
                if marker:
                    hero_markers.append({'name': marker.name, 'count': marker.count})
    
    all_markers = Marker.query.all()
    all_equipment = Equipment.query.all()
    all_skills = Skill.query.all()
    
    return render_template('index_local.html',
                         all_markers=all_markers,
                         all_equipment=all_equipment,
                         all_skills=all_skills,
                         current_hero=hero,
                         current_hero_skills=current_hero_skills,
                         hero_markers=hero_markers)

@bp.route('/skills')
def skills():
    skill_type = request.args.get('type')
    search = request.args.get('search', '')

    query = Skill.query
    if search:
        query = query.filter(Skill.name.contains(search))
    if skill_type:
        query = query.filter_by(skill_type=skill_type)

    skills_list = query.all()
    return render_template('skills.html', skills=skills_list,
                         skill_type=skill_type, search=search)

@bp.route('/skills/add', methods=['GET', 'POST'])
def add_skill():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        skill_type = request.form.get('skill_type', '普通技')

        existing = Skill.query.filter_by(name=name).first()
        if existing:
            return render_template('skill_edit.html', skill=existing, error='技能名已存在')

        skill = Skill(name=name, description=description, skill_type=skill_type)
        db.session.add(skill)
        db.session.commit()
        return redirect(url_for('routes.skills'))

    return render_template('skill_edit.html', skill=None)

@bp.route('/skills/edit/<int:id>', methods=['GET', 'POST'])
def edit_skill(id):
    skill = Skill.query.get_or_404(id)
    if request.method == 'POST':
        skill.name = request.form['name']
        skill.description = request.form['description']
        skill.skill_type = request.form.get('skill_type', '普通技')
        db.session.commit()
        return redirect(url_for('routes.skills'))
    return render_template('skill_edit.html', skill=skill)

@bp.route('/skills/delete/<int:id>', methods=['POST'])
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    return redirect(url_for('routes.skills'))

@bp.route('/heroes')
def heroes():
    camp = request.args.get('camp')
    tag = request.args.get('tag')
    search = request.args.get('search', '')

    query = Hero.query
    if search:
        query = query.filter(Hero.name.contains(search))
    if camp:
        query = query.filter_by(camp=camp)
    if tag:
        query = query.filter_by(tag=tag)

    heroes_list = query.all()
    return render_template('heroes.html', heroes=heroes_list, camp=camp, tag=tag, search=search)

@bp.route('/heroes/add', methods=['GET', 'POST'])
def add_hero():
    all_skills = Skill.query.all()
    
    if request.method == 'POST':
        name = request.form['name']
        camp = request.form['camp']
        hp = int(request.form['hp'])
        tag = request.form.get('tag', '标')
        
        existing = Hero.query.filter_by(name=name).first()
        if existing:
            return render_template('hero_edit.html', hero=None, all_skills=all_skills, error='武将名已存在')
        
        hero = Hero(name=name, camp=camp, hp=hp, tag=tag)
        db.session.add(hero)
        db.session.flush()
        
        selected_skills = request.form.getlist('skills')
        for skill_name in selected_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if skill:
                hero.skills.append(skill)
        
        db.session.commit()
        return redirect(url_for('routes.heroes'))
    
    return render_template('hero_edit.html', hero=None, all_skills=all_skills)

@bp.route('/heroes/<int:id>')
def hero_detail(id):
    hero = Hero.query.get_or_404(id)
    
    hero_pool = HeroPool.query.filter_by(hero_name=hero.name).all()
    skill_pool = SkillPool.query.filter_by(hero_name=hero.name).all()
    marker_pool = HeroMarkerPool.query.filter_by(hero_name=hero.name).all()
    
    hero_detail = HeroDetail.query.filter_by(hero_name=hero.name).first()
    
    hero_pool_heroes = []
    for hp in hero_pool:
        h = Hero.query.filter_by(name=hp.pool_hero_name).first()
        if h:
            hero_pool_heroes.append(h)
    
    skill_pool_skills = []
    for sp in skill_pool:
        s = Skill.query.filter_by(name=sp.skill_name).first()
        if s:
            skill_pool_skills.append(s)
    
    marker_pool_markers = []
    for mp in marker_pool:
        m = Marker.query.filter_by(name=mp.marker_name).first()
        if m:
            marker_pool_markers.append(m)
    
    return render_template('hero_detail.html', 
                         hero=hero,
                         hero_pool=hero_pool_heroes,
                         skill_pool=skill_pool_skills,
                         marker_pool=marker_pool_markers,
                         hero_detail=hero_detail)

@bp.route('/heroes/edit/<int:id>', methods=['GET', 'POST'])
def edit_hero(id):
    hero = Hero.query.get_or_404(id)
    all_skills = Skill.query.all()

    if request.method == 'POST':
        hero.name = request.form['name']
        hero.camp = request.form['camp']
        hero.hp = int(request.form['hp'])
        hero.tag = request.form.get('tag', '标')

        hero.skills.clear()
        selected_skills = request.form.getlist('skills')
        for skill_name in selected_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if skill:
                hero.skills.append(skill)

        db.session.commit()
        return redirect(url_for('routes.heroes'))

    return render_template('hero_edit.html', hero=hero, all_skills=all_skills)

@bp.route('/heroes/delete/<int:id>', methods=['POST'])
def delete_hero(id):
    hero = Hero.query.get_or_404(id)
    db.session.delete(hero)
    db.session.commit()
    return redirect(url_for('routes.heroes'))

@bp.route('/select_hero_for_local/<int:id>')
def select_hero_for_local(id):
    return redirect(url_for('routes.index_local', hero_id=id))

@bp.route('/save_hero_detail', methods=['POST'])
def save_hero_detail():
    hero_name = request.form['hero_name']
    avatar_url = request.form.get('avatar_url', '')
    rating = float(request.form.get('rating', 0))
    review = request.form.get('review', '')
    hero_id = request.form.get('hero_id')
    
    hero_detail = HeroDetail.query.filter_by(hero_name=hero_name).first()
    if hero_detail:
        hero_detail.avatar_url = avatar_url
        hero_detail.rating = rating
        hero_detail.review = review
    else:
        hero_detail = HeroDetail(hero_name=hero_name, avatar_url=avatar_url, rating=rating, review=review)
        db.session.add(hero_detail)
    
    db.session.commit()
    
    # 检查是否是 AJAX 请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
        return jsonify({'success': True, 'hero_id': hero_id})
    return redirect(url_for('routes.hero_detail', id=hero_id))

@bp.route('/skill_pool')
def skill_pool():
    hero_name = request.args.get('hero')
    heroes = Hero.query.all()
    
    skill_pool_list = []
    hero_pool_list = []
    marker_pool_list = []
    
    if hero_name:
        pool_skills = SkillPool.query.filter_by(hero_name=hero_name).all()
        for ps in pool_skills:
            skill = Skill.query.filter_by(name=ps.skill_name).first()
            skill_pool_list.append({
                'id': ps.id,
                'skill_name': ps.skill_name,
                'description': skill.description if skill else '',
                'skill_type': skill.skill_type if skill else ''
            })
        
        pool_heroes = HeroPool.query.filter_by(hero_name=hero_name).all()
        for ph in pool_heroes:
            hero = Hero.query.filter_by(name=ph.pool_hero_name).first()
            if hero:
                hero_pool_list.append({
                    'id': ph.id,
                    'hero_name': ph.pool_hero_name,
                    'camp': hero.camp,
                    'hp': hero.hp
                })
        
        pool_markers = HeroMarkerPool.query.filter_by(hero_name=hero_name).all()
        for pm in pool_markers:
            marker = Marker.query.filter_by(name=pm.marker_name).first()
            marker_pool_list.append({
                'id': pm.id,
                'marker_name': pm.marker_name,
                'count': marker.count if marker else 0
            })
    
    all_skills = Skill.query.all()
    all_heroes_for_pool = Hero.query.all()
    all_markers = Marker.query.all()
    
    return render_template('skill_pool.html', 
                          skill_pool=skill_pool_list,
                          hero_pool=hero_pool_list,
                          marker_pool=marker_pool_list,
                          hero_name=hero_name,
                          heroes=heroes,
                          all_skills=all_skills,
                          all_heroes=all_heroes_for_pool,
                          all_markers=all_markers)

@bp.route('/skill_pool/add_skill', methods=['POST'])
def add_skill_to_pool():
    skill_name = request.form['skill_name']
    hero_name = request.form.get('hero_name')
    
    existing = SkillPool.query.filter_by(skill_name=skill_name, hero_name=hero_name).first()
    if skill_name and not existing:
        pool_skill = SkillPool(skill_name=skill_name, hero_name=hero_name)
        db.session.add(pool_skill)
        db.session.commit()
    
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/remove_skill/<int:id>', methods=['POST'])
def remove_skill_from_pool(id):
    pool_skill = SkillPool.query.get_or_404(id)
    hero_name = pool_skill.hero_name
    db.session.delete(pool_skill)
    db.session.commit()
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/add_all_skills', methods=['POST'])
def add_all_skills_to_pool():
    skill_type = request.form.get('skill_type', 'all')
    hero_name = request.form.get('hero_name')
    
    if skill_type == 'all':
        skills = Skill.query.all()
    else:
        skills = Skill.query.filter_by(skill_type=skill_type).all()

    for skill in skills:
        existing = SkillPool.query.filter_by(skill_name=skill.name, hero_name=hero_name).first()
        if not existing:
            pool_skill = SkillPool(skill_name=skill.name, hero_name=hero_name)
            db.session.add(pool_skill)
    db.session.commit()
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/add_hero', methods=['POST'])
def add_hero_to_pool():
    pool_hero_name = request.form['pool_hero_name']
    hero_name = request.form.get('hero_name')
    
    existing = HeroPool.query.filter_by(pool_hero_name=pool_hero_name, hero_name=hero_name).first()
    if pool_hero_name and not existing:
        pool_hero = HeroPool(pool_hero_name=pool_hero_name, hero_name=hero_name)
        db.session.add(pool_hero)
        db.session.commit()
    
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/remove_hero/<int:id>', methods=['POST'])
def remove_hero_from_pool(id):
    pool_hero = HeroPool.query.get_or_404(id)
    hero_name = pool_hero.hero_name
    db.session.delete(pool_hero)
    db.session.commit()
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/add_all_heroes', methods=['POST'])
def add_all_heroes_to_pool():
    camp = request.form.get('camp', 'all')
    hero_name = request.form.get('hero_name')
    
    if camp == 'all':
        heroes = Hero.query.all()
    else:
        heroes = Hero.query.filter_by(camp=camp).all()

    for hero in heroes:
        existing = HeroPool.query.filter_by(pool_hero_name=hero.name, hero_name=hero_name).first()
        if not existing:
            pool_hero = HeroPool(pool_hero_name=hero.name, hero_name=hero_name)
            db.session.add(pool_hero)
    db.session.commit()
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/add_marker', methods=['POST'])
def add_marker_to_pool():
    marker_name = request.form['marker_name']
    hero_name = request.form.get('hero_name')
    
    existing = HeroMarkerPool.query.filter_by(marker_name=marker_name, hero_name=hero_name).first()
    if marker_name and not existing:
        pool_marker = HeroMarkerPool(marker_name=marker_name, hero_name=hero_name)
        db.session.add(pool_marker)
        db.session.commit()
    
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/remove_marker/<int:id>', methods=['POST'])
def remove_marker_from_pool(id):
    pool_marker = HeroMarkerPool.query.get_or_404(id)
    hero_name = pool_marker.hero_name
    db.session.delete(pool_marker)
    db.session.commit()
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/skill_pool/add_all_markers', methods=['POST'])
def add_all_markers_to_pool():
    hero_name = request.form.get('hero_name')
    markers = Marker.query.all()

    for marker in markers:
        existing = HeroMarkerPool.query.filter_by(marker_name=marker.name, hero_name=hero_name).first()
        if not existing:
            pool_marker = HeroMarkerPool(marker_name=marker.name, hero_name=hero_name)
            db.session.add(pool_marker)
    db.session.commit()
    return redirect(url_for('routes.skill_pool', hero=hero_name))

@bp.route('/markers', methods=['GET', 'POST'])
def markers():
    if request.method == 'POST':
        action = request.form.get('action')
        marker_name = request.form.get('marker_name')
        marker = Marker.query.filter_by(name=marker_name).first()

        if action == 'add':
            if marker:
                marker.count += 1
            else:
                marker = Marker(name=marker_name, count=1)
                db.session.add(marker)
        elif action == 'remove':
            if marker and marker.count > 0:
                marker.count -= 1
        elif action == 'set':
            count = int(request.form.get('count', 0))
            if marker:
                marker.count = count
            else:
                marker = Marker(name=marker_name, count=count)
                db.session.add(marker)
        elif action == 'delete':
            if marker:
                db.session.delete(marker)

        db.session.commit()
        return redirect(url_for('routes.markers'))

    markers_list = Marker.query.all()
    return render_template('markers.html', markers=markers_list)

@bp.route('/markers/add', methods=['POST'])
def add_marker():
    name = request.form['name']
    count = int(request.form.get('count', 0))
    
    existing = Marker.query.filter_by(name=name).first()
    if existing:
        return redirect(url_for('routes.markers'))
    
    marker = Marker(name=name, count=count)
    db.session.add(marker)
    db.session.commit()
    return redirect(url_for('routes.markers'))

@bp.route('/cards')
def cards():
    card_type = request.args.get('type')
    search = request.args.get('search', '')

    query = Card.query
    if search:
        query = query.filter(Card.name.contains(search))
    if card_type:
        query = query.filter_by(card_type=card_type)

    cards_list = query.all()
    return render_template('cards.html', cards=cards_list, card_type=card_type, search=search)

@bp.route('/cards/add', methods=['POST'])
def add_card():
    name = request.form['name']
    card_type = request.form.get('card_type', '基本牌')
    description = request.form.get('description', '')
    
    existing = Card.query.filter_by(name=name).first()
    if existing:
        return redirect(url_for('routes.cards'))
    
    card = Card(name=name, card_type=card_type, description=description)
    db.session.add(card)
    db.session.commit()
    return redirect(url_for('routes.cards'))

@bp.route('/cards/delete/<int:id>', methods=['POST'])
def delete_card(id):
    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('routes.cards'))

@bp.route('/equipment')
def equipment():
    equip_type = request.args.get('type')
    search = request.args.get('search', '')

    query = Equipment.query
    if search:
        query = query.filter(Equipment.name.contains(search))
    if equip_type:
        query = query.filter_by(equip_type=equip_type)

    equipment_list = query.all()
    return render_template('equipment.html', equipment=equipment_list,
                          equip_type=equip_type, search=search)

@bp.route('/equipment/add', methods=['POST'])
def add_equipment():
    name = request.form['name']
    equip_type = request.form.get('equip_type', '武器')
    description = request.form.get('description', '')
    
    existing = Equipment.query.filter_by(name=name).first()
    if existing:
        return redirect(url_for('routes.equipment'))
    
    equip = Equipment(name=name, equip_type=equip_type, description=description)
    db.session.add(equip)
    db.session.commit()
    return redirect(url_for('routes.equipment'))

@bp.route('/equipment/delete/<int:id>', methods=['POST'])
def delete_equipment(id):
    equip = Equipment.query.get_or_404(id)
    db.session.delete(equip)
    db.session.commit()
    return redirect(url_for('routes.equipment'))

@bp.route('/equipment/toggle/<int:id>', methods=['POST'])
def toggle_equipment(id):
    equip = Equipment.query.get_or_404(id)
    equip.is_active = not equip.is_active
    db.session.commit()
    return redirect(url_for('routes.equipment'))

@bp.route('/api/get_hero_skills/<int:hero_id>')
def get_hero_skills(hero_id):
    hero = Hero.query.get(hero_id)
    if not hero:
        return jsonify([])
    skills = [{'name': s.name, 'description': s.description, 'type': s.skill_type} for s in hero.skills]
    return jsonify(skills)

@bp.route('/api/get_hero_pool/<hero_name>')
def get_hero_pool(hero_name):
    pool = HeroPool.query.filter_by(hero_name=hero_name).all()
    heroes = []
    for p in pool:
        hero = Hero.query.filter_by(name=p.pool_hero_name).first()
        if hero:
            heroes.append({'id': hero.id, 'name': hero.name, 'camp': hero.camp, 'hp': hero.hp})
    return jsonify(heroes)

@bp.route('/api/get_skill_pool/<hero_name>')
def get_skill_pool(hero_name):
    pool = SkillPool.query.filter_by(hero_name=hero_name).all()
    skills = []
    for p in pool:
        skill = Skill.query.filter_by(name=p.skill_name).first()
        if skill:
            skills.append({'name': skill.name, 'description': skill.description, 'type': skill.skill_type})
    return jsonify(skills)

@bp.route('/api/get_marker_pool/<hero_name>')
def get_marker_pool(hero_name):
    pool = HeroMarkerPool.query.filter_by(hero_name=hero_name).all()
    markers = []
    for p in pool:
        marker = Marker.query.filter_by(name=p.marker_name).first()
        if marker:
            markers.append({'name': marker.name, 'count': marker.count})
    return jsonify(markers)

@bp.route('/api/get_hero_detail/<int:hero_id>')
def get_hero_detail(hero_id):
    hero = Hero.query.get(hero_id)
    if not hero:
        return jsonify({'error': '武将不存在'}), 404
    
    skills = [{'name': s.name, 'description': s.description, 'type': s.skill_type} for s in hero.skills]
    
    hero_pool = []
    pool_heroes = HeroPool.query.filter_by(hero_name=hero.name).all()
    for p in pool_heroes:
        h = Hero.query.filter_by(name=p.pool_hero_name).first()
        if h:
            hero_pool.append({'id': h.id, 'name': h.name, 'camp': h.camp, 'hp': h.hp})
    
    skill_pool = []
    pool_skills = SkillPool.query.filter_by(hero_name=hero.name).all()
    for p in pool_skills:
        s = Skill.query.filter_by(name=p.skill_name).first()
        if s:
            skill_pool.append({'name': s.name, 'description': s.description, 'type': s.skill_type})
    
    marker_pool = []
    pool_markers = HeroMarkerPool.query.filter_by(hero_name=hero.name).all()
    for p in pool_markers:
        m = Marker.query.filter_by(name=p.marker_name).first()
        if m:
            marker_pool.append({'name': m.name, 'count': m.count})
    
    hero_detail = HeroDetail.query.filter_by(hero_name=hero.name).first()
    detail = None
    if hero_detail:
        detail = {
            'avatar_url': hero_detail.avatar_url or '',
            'rating': float(hero_detail.rating) if hero_detail.rating is not None else 0,
            'review': hero_detail.review or ''
        }
    
    return jsonify({
        'id': hero.id,
        'name': hero.name,
        'camp': hero.camp,
        'hp': hero.hp,
        'tag': hero.tag,
        'skills': skills,
        'hero_pool': hero_pool,
        'skill_pool': skill_pool,
        'marker_pool': marker_pool,
        'detail': detail
    })