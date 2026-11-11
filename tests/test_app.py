"""Regression checks for the dependency and Dash upgrade, using the real dataset."""

import unittest

import polars as pl

from app import app, server
from pages import app_br, app_en


class AppCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.test_client()

    def test_pages_and_dash_endpoints(self):
        for path in ("/en", "/br", "/_dash-layout", "/_dash-dependencies"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                if path.startswith("/_dash-"):
                    self.assertIsNotNone(response.get_json())

    def test_root_redirects_without_overriding_the_requested_language(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["Location"], "/en")
        location = app.layout.children[0]
        self.assertNotIn("pathname", location.to_plotly_json()["props"])

    def test_filters_maps_and_pagination_in_both_languages(self):
        for page, suffix in (
            (app_en, ""),
            (app_br, "_br"),
        ):
            with self.subTest(language=page.__name__):
                award_column = "Award" + suffix
                cuisine_column = "Cuisine" + suffix
                location_column = "Location" + suffix
                for style in ("light", "open-street-map", "satellite-streets"):
                    figure, counter, cards, max_page, *_ = page.update_map_cards(
                        "All", "All", "All", "All", 1, style, None
                    )
                    self.assertEqual(len(figure.data[0].lat), page.df.height)
                    self.assertEqual(figure.layout.map.style, style)
                    self.assertIn(f"{page.df.height:,}", counter)
                    self.assertEqual(len(cards), 2)
                    self.assertEqual(max_page, (page.df.height + 3) // 4)

                row = page.df.row(0, named=True)
                expected = page.df.filter(
                    (pl.col(award_column) == row[award_column])
                    & (pl.col("Price_dollar") == row["Price_dollar"])
                    & (pl.col(cuisine_column) == row[cuisine_column])
                    & (pl.col(location_column) == row[location_column])
                )
                figure, _, _, _, *_ = page.update_map_cards(
                    row[award_column], row["Price_dollar"], row[cuisine_column],
                    row[location_column], 1, "light", None
                )
                self.assertGreater(expected.height, 0)
                self.assertEqual(len(figure.data[0].lat), expected.height)

                _, counter, *_ = page.update_map_cards(
                    "All", "All", "All", "All", 2, "light", None
                )
                self.assertTrue(counter.startswith("5-8"))
                self.assertEqual(page.all_filters(1), ("All",) * 4 + (1,))

    def test_facilities_search_in_both_languages(self):
        for page, column, term in (
            (app_en, "FacilitiesAndServices", "Car park"),
            (app_br, "FacilitiesAndServices_br", "Estacionamento"),
        ):
            with self.subTest(language=page.__name__):
                expected = page.df.filter(
                    pl.col(column).cast(pl.String).str.contains(term, literal=True)
                )
                self.assertGreater(expected.height, 0)
                figure, *_ = page.update_map_cards(
                    "All", "All", "All", "All", 1, "light", term
                )
                self.assertEqual(len(figure.data[0].lat), expected.height)
                figure, _, cards, *_ = page.update_map_cards(
                    "All", "All", "All", "All", 1, "light", "no-such-facility-928374"
                )
                self.assertEqual(sum(len(trace.lat) for trace in figure.data), 0)
                self.assertEqual(cards, [])

    def test_map_callbacks_over_http(self):
        # Exercise Dash's callback request parsing and Plotly/component serialization.
        self.client.get("/_dash-layout")
        for prefix in ("map.figure", "mapa.figure"):
            output_key = next(key for key in app.callback_map if key.startswith(".." + prefix))
            callback = app.callback_map[output_key]
            values = ["All", "All", "All", "All", 1, "light", None]
            inputs = [dict(item, value=value) for item, value in zip(callback["inputs"], values)]
            response = self.client.post("/_dash-update-component", json={
                "output": output_key,
                "outputs": [
                    {"id": output.component_id, "property": output.component_property}
                    for output in callback["output"]
                ],
                "inputs": inputs,
                "state": [],
                "changedPropIds": [inputs[0]["id"] + ".value"],
            })
            with self.subTest(callback=prefix):
                self.assertEqual(response.status_code, 200)
                figure = response.get_json()["response"][prefix.split(".")[0]]["figure"]
                self.assertEqual(figure["data"][0]["type"], "scattermap")


if __name__ == "__main__":
    unittest.main()
