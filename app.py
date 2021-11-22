#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    web_link = db.Column(db.String(120))
    seek_desc = db.Column(db.String(500))
    looking_for_talent = db.Column(db.Boolean,default=False)
    genres_categories = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    related_programs = db.relationship('Program', backref='venue', lazy=True)
    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    related_programs = db.relationship('Program', backref='artist', lazy=True)
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    web_link = db.Column(db.String(120))
    seek_desc = db.Column(db.String(500))
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Program(db.Model):
    __tablename__ = 'Program'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    time_to_start = db.Column(db.DateTime,default=datetime.utcnow, nullable=False )

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]
  locs = set()
  all_venues = Venue.query.all()
  for venue in all_venues:
    locs.add((venue.city, venue.state))
  for loc in locs:
      data.append({
          "city": loc[0],
          "state": loc[1],
          "venues": []
      })
  for venue in all_venues:
      num_upcoming_programs = 0
      programs = Program.query.filter_by(venue_id=venue.id).all()
      now_date = datetime.now()

      for program in programs:
        if program.time_to_start > now_date:
            num_upcoming_programs += 1

      for venue_loc in data:
        if venue.state == venue_loc['state'] and venue.city == venue_loc['city']:
          venue_loc['venues'].append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": num_upcoming_programs
          })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_query_term = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike(f'%{search_query_term}%'))

  response={
    "count": results.count(),
    "data": results
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  particular_venue = Venue.query.get(venue_id)
  programs = Program.query.filter_by(venue_id=venue_id).all()
  prev_programs = []
  future_programs = []
  time_now = datetime.now()

  for program in programs:
    data = {
          "artist_id": program.artist_id,
          "artist_name": program.artist.name,
           "program": program.artist.image_link,
           "start_time": format_datetime(str(program.time_to_start))
        }
    if program.time_to_start > time_now:
      future_programs.append(data)
    else:
      prev_programs.append(data)

  data={
    "id": particular_venue.id,
    "name": particular_venue.name,
    "genres": particular_venue.genres_categories,
    "address": particular_venue.address,
    "city": particular_venue.city,
    "state": particular_venue.state,
    "phone": particular_venue.phone,
    "website_link": particular_venue.web_link,
    "facebook_link": particular_venue.facebook_link,
    "seeking_talent": particular_venue.looking_for_talent,
    "seeking_description":particular_venue.seek_desc,
    "image_link": particular_venue.image_link,
    "past_shows": prev_programs,
    "upcoming_shows": future_programs,
    "past_shows_count": len(prev_programs),
    "upcoming_shows_count": len(future_programs),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      # get form data and create 
    form = VenueForm()
    venue_instance = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,phone=form.phone.data, image_link=form.image_link.data,genres_categories=form.genres.data, facebook_link=form.facebook_link.data, seek_desc=form.seeking_description.data,
                  web_link=form.website_link.data, looking_for_talent=form.seeking_talent.data)
    # on successful db insert, flash success
    db.session.add(venue_instance)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    # catching error exception
    db.session.rollback()
    flash('An error occurred while creating venue')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  try:
    # Get venue by ID
    particular_venue = Venue.query.get(venue_id)
    db.session.delete(particular_venue)
    db.session.commit()

    flash('Desired Venue  was deleted successfully')
  except:
    flash('An error occurred while delting venue')
    db.session.rollback()
  finally:
    db.session.close()
  
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 # array of artisits
  data = []

  all_artists = Artist.query.all()

  for particular_artist in all_artists:
    data.append({
        "id": particular_artist.id,
        "name": particular_artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_query_term = request.form.get('search_term', '')

  results = Artist.query.filter(Artist.name.ilike(f'%{search_query_term}%'))
  # filling object of data with search information
  response={
    "count": results.count(),
    "data": results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  particular_artist = Artist.query.get(artist_id)
  programs = Program.query.filter_by(artist_id=artist_id).all()
  prev_programs = []
  future_programs = []
  time_now= datetime.now()

  # Filter programs at venues wrt artist id
  for program in programs:
    data = {
          "venue_id": program.venue_id,
          "venue_name": program.venue.name,
          "venue_image_link": program.venue.image_link,
          "start_time": format_datetime(str(program.time_to_start))
        }
    if program.time_to_start > time_now:
      future_programs.append(data)
    else:
      prev_programs.append(data)

  data={
    "id": particular_artist.id,
    "name": particular_artist.name,
    "genres": particular_artist.genres,
    "city": particular_artist.city,
    "state": particular_artist.state,
    "phone": particular_artist.phone,
    "facebook_link": particular_artist.facebook_link,
    "image_link": particular_artist.image_link,
    "past_shows": prev_programs,
    "upcoming_shows": future_programs,
    "past_shows_count": len(prev_programs),
    "upcoming_shows_count": len(future_programs),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #get artist based on id
  particular_artist = Artist.query.get(artist_id)
  artist={
    "id": particular_artist.id,
    "name": particular_artist.name,
    "genres": particular_artist.genres,
    "city": particular_artist.city,
    "state": particular_artist.city,
    "phone": particular_artist.phone,
    "facebook_link": particular_artist.facebook_link,
     "image_link": particular_artist.image_link,
     "website_link": particular_artist.web_link,
    "seeking_description": particular_artist.seek_desc,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()

    particular_artist = Artist.query.get(artist_id)
    particular_artist.name = form.name.data
    particular_artist.name = form.name.data
    particular_artist.phone = form.phone.data
    particular_artist.state = form.state.data
    particular_artist.city = form.city.data
    particular_artist.genres = form.genres.data
    particular_artist.image_link = form.image_link.data
    particular_artist.facebook_link = form.facebook_link.data
    particular_artist.web_link = form.website_link.data
    particular_artist.seek_desc = form.seeking_description.data
    
    db.session.commit()
    flash('The Artist data has been successfully updated!')
  except:
    flash('An Error occured and the update was unsuccessful')
    db.session.rolback()
   
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_to_be_edited = Venue.query.get(venue_id)
  venue_to_be_edited={
    "id": venue_to_be_edited.id,
    "name": venue_to_be_edited.name,
    "genres": venue_to_be_edited.genres_categories,
    "address": venue_to_be_edited.address,
    "city": venue_to_be_edited.city,
    "state": venue_to_be_edited.state,
    "phone": venue_to_be_edited.phone,
    "website_link": venue_to_be_edited.web_link,
    "facebook_link": venue_to_be_edited.facebook_link,
    "seeking_talent": venue_to_be_edited.looking_for_talent,
    "seeking_description": venue_to_be_edited.seek_desc,
    "image_link": venue_to_be_edited.image_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_to_be_edited)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  try:
    venue_to_be_edited = Venue.query.get(venue_id)
    name = form.name.data

    venue_to_be_edited.name = name
    venue_to_be_edited.genres_categories = form.genres.data
    venue_to_be_edited.city = form.city.data
    venue_to_be_edited.state = form.state.data
    venue_to_be_edited.address = form.address.data
    venue_to_be_edited.phone = form.phone.data
    venue_to_be_edited.facebook_link = form.facebook_link.data
    venue_to_be_edited.web_link = form.website_link.data
    venue_to_be_edited.image_link = form.image_link.data
    venue_to_be_edited.looking_for_talent = form.seeking_talent.data
    venue_to_be_edited.seek_desc = form.seeking_description.data

    db.session.commit()
    flash('Particular Venue  has been updated')
  except:
    db.session.rollback()
    flash('Error while updating venue')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()

  try:
    artist = Artist(name=form.name.data.strip(), city=form.city.data.strip(), state=form.city.data, phone=form.phone.data, genres=form.genres.data, 
                    image_link=form.image_link.data, facebook_link=form.facebook_link.data,web_link=form.website_link.data,seek_desc= form.seeking_description.data)
    
    db.session.add(artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Artist was successfully created!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be created.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')
#newly added route for deleting th artist wit artist id
@app.route('/artist/<artist_id>', methods=['DELETE'])
def remove_artist(artist_id):
  try:

    particular_artist = Artist.query.get(artist_id)
    db.session.delete(particular_artist)
    db.session.commit()

    flash('Particular artist was deleted')
  except:
    flash('An error occured and Artist  could not be deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  programs = Program.query.order_by(Program.time_to_start)

  data = []

  for program in programs:
    data.append({
        "venue_id": program.venue_id,
        "venue_name": program.venue.name,
        "artist_id": program.artist_id,
        "artist_name": program.artist.name,
        "artist_image_link": program.artist.image_link,
        "start_time": format_datetime(str(program.time_to_start))
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    program = Program(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'],
                time_to_start=request.form['start_time'])

    db.session.add(program)
    db.session.commit()


  # on successful db insert, flash success
    flash('Program was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Program could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
