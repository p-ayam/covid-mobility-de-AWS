## Story of a [Data Dashboard](http://ec2-18-159-45-234.eu-central-1.compute.amazonaws.com:8050/): <br> Google Users' Mobility in Germany During the Covid-19 Pandemic


In 2020, Google released [Community Mobility Reports](https://support.google.com/covid19-mobility/answer/9824897?hl=en&ref_topic=9822927)
which is an [aggregated, anonymized dataset](https://www.youtube.com/watch?v=FfAdemDkLsc&feature=youtu.be&ab_channel=Google) from the location of its users who had turned their “Location History” setting on. The dataset reveals the changes in mobility trends during the Covid-19 pandemic across six categories of places, namely

1. groceries and pharmacies,
2. parks,
3. transit stations,
4. retail and recreation,
5. residential,
6. workplaces.

The mobility changes are represented for each day of the week in the form of a percentile change compared to the mobility on the same day of the week during the “baseline” period. The baseline can perhaps be naively branded as a representation of the pre-pandemic trends. It is calculated for each day of the week as the median of that day, chosen from the 5-week period between Jan 3rd till Feb 6th, 2020.

Coming across this dataset, I decided to combine it with the data provided by the [Robert Koch Institute](https://www.arcgis.com/home/item.html?id=f10774f1c63e40168479a1feb6c7ca74) in order to show an overlay of the temporal trends in corona-positive cases (Meldung) with the mobility across the 16 states of Germany (Bundesländer). The corona-positive cases (Meldung) are presented per 100’000 inhabitants such that the sum of the most recent 7 days provides the corresponding seven-day incidence rate.

The [dashboard](http://ec2-18-159-45-234.eu-central-1.compute.amazonaws.com:8050/) application is containerized by [Docker](https://www.docker.com/) and deployed to the [AWS Elastic Container Service (ECS)](https://aws.amazon.com/ecs/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc&ecs-blogs.sort-by=item.additionalFields.createdDate&ecs-blogs.sort-order=desc) and is updated on a daily basis. I hope the trends visualized on this dashboard, along with a knowledge of the local or national public holidays, and weather conditions can provide deeper insights into the slowing of the pathogen’s spreading across Germany. The dashboard is based on a Python code presented in the app folder (application.py).


Last but not least, I want to give a big shout-out to [Charming Data](https://www.youtube.com/channel/UCqBFsuAz41sqWcFjZkqmJqQ/featured) for the wonderful Dash Plotly tutorials.
