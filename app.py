#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  locals = []
  venues = Venue.query.all()
  for place in Venue.query.distinct(Venue.city, Venue.state).all():
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  foundedVenues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  countVenues = len(foundedVenues)
  response={
    "count": countVenues,
    "data": foundedVenues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', '') )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
      filter(
          Show.venue_id == venue_id,
          Show.artist_id == Artist.id,
          Show.start_time < datetime.now()
      ).\
      all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
      filter(
          Show.venue_id == venue_id,
          Show.artist_id == Artist.id,
          Show.start_time > datetime.now()
      ).\
      all()

  data = {
          'id': venue.id,
          "name": venue.name,
          "genres": venue.genres,
          "address": venue.address,
          "city": venue.city,
          "state": venue.state,
          "phone": venue.phone,
          "website": venue.website,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link,
          'past_shows': [{
              'artist_id': artist.id,
              'artist_image_link': artist.image_link,
              'artist_name': artist.name, 
              'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for artist, show in past_shows],
          'upcoming_shows': [{
              'artist_id': artist.id,
              'artist_image_link': artist.image_link,
              'artist_name': artist.name, 
              'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for artist, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
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
  form = VenueForm(request.form)
  try:
      venueinsert = Venue(
            name=form.name.data,
            city=form.city.data,
            state = form.state.data,
            address = form.address.data,
            phone = form.phone.data,
            image_link = form.image_link.data,
            website = form.website.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data,
            seeking_talent = form.seeking_talent.data,
            seeking_description = form.seeking_talent_description.data
        )
      db.session.add(venueinsert)
      db.session.commit()
       # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
      print(e)
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
      
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  foundedArtist = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  countArtist = len(foundedArtist)
  response={
    "count": countArtist,
    "data": foundedArtist
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
      filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.start_time < datetime.now()
      ).\
      all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
      filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.start_time > datetime.now()
      ).\
      all()

  data = {
          'id': artist.id,
          "name": artist.name,
          "genres": artist.genres,
          "city": artist.city,
          "state": artist.state,
          "phone": artist.phone,
          "website": artist.website,
          "facebook_link": artist.facebook_link,
          "seeking_venue": artist.seeking_venue,
          "seeking_description": artist.seeking_description,
          "image_link": artist.image_link,
          'past_shows': [{
              'venue_id': venue.id,
              'venue_image_link': venue.image_link,
              'venue_name': venue.name, 
              'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for venue, show in past_shows],
          'upcoming_shows': [{
              'venue_id': venue.id,
              'venue_image_link': venue.image_link,
              'venue_name': venue.name, 
              'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for venue, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
      }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
      artistinsert = Artist(
            name=form.name.data,
            city=form.city.data,
            state = form.state.data,
            phone = form.phone.data,
            genres = form.genres.data,
            image_link = form.image_link.data,
            facebook_link = form.facebook_link.data, 
            website = form.website.data,
            seeking_venue = form.seeking_venue.data, 
            seeking_description = form.seeking_venue_description.data, 
        )
      db.session.add(artistinsert)
      db.session.commit()
       # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
      print(e)
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
      
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    try:
        all_shows = Show.query.all()
        for show in all_shows:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            venue = Venue.query.filter_by(id=show.venue_id).first()
            starttimetr = str(show.start_time)
            data.append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": starttimetr
            })
    except ValueError as e:
        print(e)
        #pass
    return render_template("pages/shows.html", shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        showsinsert = Show(
              start_time = form.start_time.data,
              artist_id =form.artist_id.data,
              venue_id =form.venue_id.data
              
          )
        db.session.add(showsinsert)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except ValueError as e:
        print(e)
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
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
