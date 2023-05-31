from django.test import TestCase
from django.urls import reverse
from unittest import mock

from georiviere.contribution.models import (Contribution, ContributionQuality, ContributionLandscapeElements,
                                            ContributionQuantity, ContributionFaunaFlora, ContributionPotentialDamage)
from georiviere.contribution.tests.factories import ContributionFactory, ContributionQuantityFactory
from georiviere.portal.tests.factories import PortalFactory


class ContributionViewPostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portal = PortalFactory.create()

    def test_contribution_structure(self):
        url = reverse('api_portal:contributions-json_schema',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(set(response.json().keys()), {'type', 'required', 'properties', 'allOf'})

    def test_contribution_landscape_element(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Élément Paysagers",'
                                                             '"type": "Doline"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionLandscapeElements.objects.count(), 1)
        contribution = Contribution.objects.first()
        landscape_element = contribution.landscape_element
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(landscape_element.get_type_display(), 'Doline')

    def test_contribution_quality(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Qualité",'
                                                             '"type": "Pollution"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionQuality.objects.count(), 1)
        contribution = Contribution.objects.first()
        quality = contribution.quality
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(quality.get_type_display(), 'Pollution')

    def test_contribution_quantity(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Quantité",'
                                                             '"type": "A sec"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionQuantity.objects.count(), 1)
        contribution = Contribution.objects.first()
        quantity = contribution.quantity
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(quantity.get_type_display(), 'A sec')

    def test_contribution_faunaflora(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(4 43.5)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Faune-Flore",'
                                                             '"type": "Espèce invasive",'
                                                             '"description": "test"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionFaunaFlora.objects.count(), 1)
        contribution = Contribution.objects.first()
        fauna_flora = contribution.fauna_flora
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(fauna_flora.get_type_display(), 'Espèce invasive')

    def test_contribution_potential_damages(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(4 42.5)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Dégâts Potentiels",'
                                                             '"type": "Éboulements"}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContributionPotentialDamage.objects.count(), 1)
        contribution = Contribution.objects.first()
        potential_damage = contribution.potential_damage
        self.assertEqual(contribution.email_author, 'x@x.x')
        self.assertEqual(potential_damage.get_type_display(), 'Éboulements')

    def test_contribution_category_does_not_exist(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Foo"}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'properties': ["'Foo' is not one of "
                                                          "['Contribution Quantité', "
                                                          "'Contribution Qualité', "
                                                          "'Contribution Faune-Flore', "
                                                          "'Contribution Élément Paysagers', "
                                                          "'Contribution Dégâts Potentiels']"]})

    @mock.patch('georiviere.contribution.schema.get_contribution_properties')
    def test_contribution_category_model_does_not_exist(self, mocked):
        def json_property():
            json_schema_properties = {'name_author': {
                'type': "string",
                'title': "Name author",
                "maxLength": 128
            }, 'first_name_author': {
                'type': "string",
                'title': "First name author",
                "maxLength": 128
            }, 'email_author': {
                'type': "string",
                'title': "Email",
                'format': "email"
            }, 'date_observation': {
                'type': "string",
                'title': "Observation's date",
                'format': 'date'
            }, 'description': {
                'type': "string",
                'title': 'Description'
            }, 'category': {
                "type": "string",
                "title": "Category",
                "enum": [
                    'foo',
                ],
            }
            }
            return json_schema_properties
        mocked.side_effect = json_property
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "foo"}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'Error': "La catégorie n'est pas valide"})

    @mock.patch('georiviere.contribution.schema.get_contribution_allOf')
    def test_contribution_category_model_other_error(self, mocked):
        def json_property():
            json_schema_all_of = [{'if': {'properties': {'category': {'const': 'Contribution Quantité'}}},
                                   'then': {'properties': {'type': {'type': 'string', 'title': 'Type',
                                                                    'enum': ['Landing', ]}}}}]
            return json_schema_all_of

        mocked.side_effect = json_property
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.post(url, data={"geom": "POINT(0 0)",
                                               "properties": '{"email_author": "x@x.x",  "date_observation": "2022-08-16", '
                                                             '"category": "Contribution Quantité",'
                                                             '"type": "Landing"}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'Error': "KeyError 'Landing'"})


class ContributionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portal = PortalFactory.create()
        cls.contribution = ContributionFactory.create(published=True, portal=cls.portal, description="foo")
        cls.contribution_other_portal = ContributionFactory.create(published=True)
        cls.contribution_not_published = ContributionFactory.create(published=False, portal=cls.portal)
        cls.contribution_quantity = ContributionQuantityFactory.create(contribution=cls.contribution)
        cls.other_contribution_quantity = ContributionQuantityFactory.create(
            contribution=cls.contribution_not_published)
        cls.other_contribution_quantity_2 = ContributionQuantityFactory.create(
            contribution=cls.contribution_other_portal)

    def test_contribution_list(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertDictEqual(response.json()[0], {'category': 'Contribution Quantité',
                                                  'description': 'foo', 'type': 'A sec'})

    def test_contribution_detail(self):
        url = reverse('api_portal:contributions-detail',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'pk': self.contribution.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(set(response.json()), {'category', 'description', 'type'})

    def test_contribution_geojson_list(self):
        url = reverse('api_portal:contributions-list',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr',
                              'format': 'geojson'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(set(response.json().keys()), {'features', 'type'})

    def test_contribution_geojson_detail(self):
        url = reverse('api_portal:contributions-detail',
                      kwargs={'portal_pk': self.portal.pk, 'lang': 'fr', 'pk': self.contribution.pk,
                              'format': 'geojson'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(set(response.json().keys()), {'id', 'type', 'geometry', 'properties'})
        self.assertSetEqual(set(response.json()['properties']), {'category', })
