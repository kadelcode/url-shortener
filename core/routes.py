import json
from datetime import datetime
from core.models import ShortUrls, CustomShortUrls, User
from core.forms import LoginForm, RegistrationForm, EditProfileForm
from core import app, db, login_manager
from random import choice
import string, hashlib
import codecs
from flask import render_template, request, flash, redirect, url_for, g
from flask_login import login_user, login_required, logout_user, current_user
from bleach import clean

# Choice algorithm
def generate_short_id(num_of_chars: int):
    """Function to generate short_id of specified number of characters"""
    return ''.join(choice(string.ascii_letters+string.digits) for _ in range(num_of_chars))

# Hashlib algorithm
def generate_short_url(custom_url):
    """ Generates a short custom URL
    from a long string
    
    Keyword arguments:
    argument -- The long link to generate the short URL from.
    Return: A short custom url
    """

    # Generate a hash of the custom URL
    hash = hashlib.sha256(custom_url.encode('utf-8')).hexdigest()

    # Take the first 5 characters of the hash
    short_url = hash[:5]

    return short_url
    
# Index(homepage) route
@app.route('/', methods=['GET', 'POST'])
def index():
    #if current_user is not None and current_user.is_authenticated:
    #    return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        url = request.form['url']
            
        if not url:
            flash('The URL is required!', 'error')
            return redirect(url_for('index'))

        
        short_id = generate_short_id(8)
        
        # If the original link exits, then return the short id from the database
        if ShortUrls.query.filter_by(original_url=url).first() is not None:
            flash('Link found in the database', 'info')
            short_id = ShortUrls.query.filter_by(original_url=url).first().short_id
            short_url = request.host_url + short_id
            return render_template('index.html', short_url=short_url)
        

        # If the original link doesn't exist, then add to the database
        if ShortUrls.query.filter_by(original_url=url).first() is None:
            new_link = ShortUrls(original_url=url, short_id=short_id, created_at=datetime.now())
            db.session.add(new_link)
            db.session.commit()
            short_url = request.host_url + short_id


            flash('Short link successfully created!', 'success')
            return render_template('index.html', short_url=short_url)

    return render_template('index.html')

# Redirect the short url
@app.route('/<short_id>')
def redirect_url(short_id):
    link = ShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# visit link
@app.route('/visit/<short_id>')
@login_required
def visit_link(short_id):
    user_id = current_user.id # current logged in user id
    link = CustomShortUrls.query.filter_by(user_id=user_id, short_id=short_id).first()
    if link:
        return redirect(link.original_url)

    else:
        flash('Invalid Link!', 'error')
        return redirect(url_for('index'))


# Route for registering a user to the platform
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':       
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            password1 = form.password1.data

            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
                return redirect(url_for('register'))
            
            if not password and password1:
                flash('password is required!', 'error')
                return redirect(url_for('register'))

            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! You can now login.', 'success')
            if current_user.is_authenticated:
                return redirect(url_for('user_dashboard', user=current_user.username))
            else:
                # Redirect the user to the login page.
                return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login function
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('login successful', 'success')
            return redirect(url_for('user_dashboard', user=current_user.username))
        flash('Invalid username or password!', 'error')
    return render_template('login.html', form=form)

# Logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Dashboard route
@app.route('/<user>/dashboard', methods=['GET','POST'])
@login_required
def user_dashboard(user):
    # user username
    user = current_user.username
    # A post request method to generate a custom URL for a logged in user
    if request.method == 'POST':
        url = request.form.get('url') # Required input
        domain = request.form.get('domain') # Optional but also required if the user is on a payed plan
        back_half = request.form.get('back_half')  # Optional

        short_id = generate_short_id(5) # For every post request, a short id is always generated

        # If the user doesn't enter a long URL, then this happens
        if not url:
            flash('The URL is required!', 'error')
            return redirect(url_for('user_dashboard', user=current_user.username))

        if url and not(domain) and not(back_half):
            # Get the current user id
            user_id = current_user.id

            # If the original url exits in db, then return the short url from the database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url, domain=None, back_half=None).first() is not None:
                flash("Custom URL already generated. You can copy the link below.", 'info')
                short_url = CustomShortUrls.query.filter_by(user_id=user_id,original_url=url).first().short_url

                # short_url = request.host_url + short_id
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))
            else: # if original url does exist
                short_url = request.host_url + short_id
                date_time = datetime.now()
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, short_id=short_id, short_url=short_url,created_at=date_time)
                db.session.add(custom_link)
                db.session.commit()
                flash(clean("Custom URL successfully generated. You can copy the link below."), 'success')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))

        if url and domain and not(back_half):
            # Get the current user id
            user_id = current_user.id

            # Check if url and domain already exist in database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None and \
                (CustomShortUrls.query.filter_by(user_id=user_id, domain=domain).first() is not None):
                short_url = CustomShortUrls.query.filter_by(user_id=user_id, original_url=url, domain=domain).first().short_url
                flash('Custom url already created. You can copy the link below', 'info')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))

            else:
                short_url = domain + "/" + short_id
                date_time = datetime.now()
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, domain=domain, short_id=short_id, short_url = short_url, created_at=date_time)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated. You can copy the link below.', 'success')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))

        if url and domain and back_half:
            # Get the current user id
            user_id = current_user.id

            # Check if url, domain, and back_half already in database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None and \
                (CustomShortUrls.query.filter_by(user_id=user_id, domain=domain).first() is not None) and \
                    (CustomShortUrls.query.filter_by(user_id=user_id, back_half=back_half).first() is not None):
                flash('Custom url already created. You can copy the link below.', 'info')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))
            
            else:
                short_url = domain + "/" + short_id + "/" + back_half
                date_time = datetime.now()
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, domain=domain, back_half=back_half, short_id=short_id, short_url = short_url, created_at=date_time)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated. You can copy the link below.', 'success')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))

        if url and back_half and not(domain):
            # Get the current user id
            user_id = current_user.id
            
            # Check if url and back_half exist in database
            if CustomShortUrls.query.filter_by(user_id=user_id, original_url=url).first() is not None and \
                (CustomShortUrls.query.filter_by(user_id=user_id, back_half=back_half).first() is not None):
                short_url = CustomShortUrls.query.filter_by(user_id=user_id, original_url=url, back_half=back_half).first().short_url
                flash('Custom url already created. You can copy the link below.', 'info')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))
            
            else:
                short_url = request.host_url + short_id + "/" + back_half
                date_time = datetime.now()
                custom_link = CustomShortUrls(user_id=user_id, original_url=url, back_half=back_half, short_id=short_id, short_url = short_url, created_at=date_time)
                db.session.add(custom_link)
                db.session.commit()
                flash('Custom URL successfully generated. You can copy the link below.', 'success')
                return render_template("overview.html", user=current_user.username, short_url=short_url)
                # return render_template('overview.html', user=current_user.username, short_url = short_url)
                #return redirect(url_for('user_dashboard', user=current_user.username, short_url = short_url))
        '''
        # If the original link doesn't exist, then add to the database
        if CustomShortUrls.query.filter_by(original_url=url).first() is None:
            new_link = CustomShortUrls(original_url=url, domain=domain, back_half=back_half, short_id=short_id, created_at=datetime.now())
            db.session.add(new_link)
            db.session.commit()
            short_url = request.host_url + short_id
            flash('Short custom link successfully generated', 'success')
            return render_template("overview.html", short_url=short_url)
        '''
    
    # for GET request
    return render_template('overview.html')

# Redirect the custom short url with only short_id
@app.route('/<short_id>')
def redirect_custom_url_s(short_id):
    link = CustomShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Redirect the custom short url with short_id && domain
@app.route('/<domain>/<short_id>/')
def redirect_custom_url_ds(short_id, back_half):
    link = CustomShortUrls.query.filter_by(domain=domain, short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Redirect the custom short url with short_id && back_half
@app.route('/<short_id>/<back_half>')
def redirect_custom_url_sb(short_id, back_half):
    user_id = current_user.id
    link = CustomShortUrls.query.filter_by(user_id=user_id, short_id=short_id, back_half=back_half).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Redirect the custom short url with short_id, domain && back_half
@app.route('/<domain>/<short_id>/<back_half>')
def redirect_custom_url_dsb(domain, short_id, back_half):
    link = CustomShortUrls.query.filter_by(domain=domain, short_id=short_id, back_half=back_half).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL', 'error')
        return redirect(url_for('index'))

# Route for the user generated custom URLs
@app.route('/my_custom-urls')
@login_required
def user_custom_url():
    username = current_user.username
    user_id = current_user.id
    # Get the custom urls of the particular user in reverse chronological order.
    custom_urls = CustomShortUrls.query.filter_by(user_id=user_id).order_by(CustomShortUrls.created_at.desc()).all()
    # custom_urls = User.query.get(user_id).customshorturls
    return render_template('user_custom_url.html', custom_urls=custom_urls)

# Function to delete a custom url for an authenticated user
@app.route('/delete/<short_id>')
@login_required
def delete(short_id):
    custom_url = CustomShortUrls.query.filter_by(short_id=short_id).first()

    if custom_url:
        db.session.delete(custom_url)
        db.session.commit()
        flash('successfully deleted custom url', 'success')

    else:
        flash("Couldn't delete the custom url you requested for.", 'error')

    return redirect(url_for('user_custom_url'))

# Route for the help section
@app.route('/help')
@login_required
def help():
    return render_template('help.html')

# Route for the pro version that requires payment
@app.route('/pro_version')
@login_required
def pro_version():
    return render_template('pro_version.html')

# why platform page
@app.route('/why-bitsy')
def why_bitsy():
    return render_template('why_bitsy.html')

# View user profile
@app.route('/<user>/view-profile')
@login_required
def view_profile(user):
    user = current_user.username
    return render_template('view_profile.html', user=user)

# Edit profile route
@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            username = form.username.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            
            # Get the id of the current user
            user = User.query.get(current_user.id)

            user.email = email # Update the email of the user
            user.username = username # Update the username of the user
            user.first_name = first_name # Update the first name of the user
            user.last_name = last_name # Update the last name of the user

            db.session.commit() # commit the updated user info to the database
            flash('Your profile has been updated.', 'success')
            return redirect(url_for('view_profile', user=current_user.username))
    form.email.data = current_user.email
    form.username.data = current_user.username
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name

    return render_template('edit_profile.html', form=form)
