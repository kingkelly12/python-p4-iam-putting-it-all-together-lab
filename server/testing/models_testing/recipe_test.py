import pytest
from sqlalchemy.exc import IntegrityError
from models import db, Recipe
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestRecipe:
    '''User in models.py'''

    def test_has_attributes(self, app):
        '''has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            recipe = Recipe(
                    title="Delicious Shed Ham",
                    instructions="""Or kind rest bred with am shed then. In""" + \
                        """ raptures building an bringing be. Elderly is detract""" + \
                        """ tedious assured private so to visited. Do travelling""" + \
                        """ companions contrasted it. Mistress strongly remember""" + \
                        """ up to. Ham him compass you proceed calling detract.""" + \
                        """ Better of always missed we person mr. September""" + \
                        """ smallness northward situation few her certainty""" + \
                        """ something.""",
                    minutes_to_complete=60,
                    user_id=1
                    )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something."""
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self, app):
        '''requires each record to have a title.'''

        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            recipe = Recipe()
            
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self, app):
        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            '''must raise either a sqlalchemy.exc.IntegrityError with constraints or a custom validation ValueError'''
            with pytest.raises( (IntegrityError, ValueError) ):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol")
                db.session.add(recipe)
                db.session.commit()

