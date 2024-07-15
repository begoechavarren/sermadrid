from sermadrid.pipelines import SerMadridInferencePipeline


def predict_parking_availability(
    datetime_str: str, neighbourhood_id_str: str, models: dict, spaces_dict: dict
) -> dict:
    SERMADRID_INFERENCE = SerMadridInferencePipeline()
    MODEL = models.get(neighbourhood_id_str)

    prediction = SERMADRID_INFERENCE.run(
        datetime=datetime_str,
        model=MODEL,
        num_plazas=spaces_dict[neighbourhood_id_str]["num_plazas"],
        return_percentage=True,
    )[0]
    return {
        "barrio": spaces_dict[neighbourhood_id_str]["barrio"],
        "prediction": prediction,
    }
