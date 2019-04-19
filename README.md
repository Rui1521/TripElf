# TripElf

## Authors

Zexi Han, Rui Wang, Wenyi Jin, Qinyu Chen

## Links

[Landing Page](https://tripelf.herokuapp.com/)

[About the Project](https://tripelf.herokuapp.com/about)

[Video Tutorial](https://tripelf.herokuapp.com/tutorial)

## Intro

When planning a trip to an unfamiliar city, it is always difficult to pick a short-term rental neighborhood that could give us the best experience. We present an interactive-map web application named TripElf to help travelers make decisions on this with ease. Most travelers appreciate hearing or reading others’ opinions before making a decision. And it is time-consuming to gather information about these neighborhoods. TripElf can satisfy both of the needs for travelers. It provides users with intuitive knowledge about the neighborhoods by demonstrating the machine-generated overviews of the neighborhoods, based on Airbnb listing reviews written by guests who truly experienced living in certain neighborhoods.
   
We summarized text overview of the neighborhoods with various unsupervised text modeling approaches, including KL-SUM, LDA-SUM, Summarization by Clustering Sentences Embedding, and Query-based Summarization with Word Embedding. We provide comprehensive empirical evidence showing that our machine-generated overviews are representative of the average living experience of the neighborhood. In addition, descriptive statistics of the neighborhoods from six aspects that the travelers may concern, including entertainment, transit, noise, expense, safety, and host, are also conveyed to the users. We build a React web app written with modern JavaScript for data visualization. Both high-level choropleth map and fine-grained details of the neighborhoods are demonstrated through our interactive-map web app.

## Built With

* PyTorch
* React
* Mapbox GL JS
* D3
* Flask

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details
