# Early Warning System for Fascist Speech Detection
AKA Fascist Analysis Speech Tool (FAST)

This open-source project provides an early warning system for detecting fascist rhetoric in speeches. By analyzing textual patterns, keyword frequencies, and sentiment, it offers an objective approach to identify indicators of fascist or tyrannical language. It also aims to educate the public and can assist politicians in avoiding harmful rhetoric.

The project is implemented using primarily Python with a Flask backend, a Jupyter Notebook for initial data exploration and analysis, and React JavaScript frontend for visualizing results. It is released under the MIT License.

Try the tool on github pages [here](https://colliecoder.github.io/FAST/)

## What is Fascism/Historical Context


## Features

Based on historic context, we look at six primary traits commonly found in fascist speeches:
- **Glorification of a Past Golden Age**: An idealized, nostalgic past. Can signify the rewriting of historical fact.
- **Us vs. Them Mentality**: Divisive language targeting or identifying specific groups or political opponents. Differentiation from "an other" group.
- **Cult of Personality**: References that elevate the leader above all else such as mentions of a leader being a savior.
- **Militarism or Violence**: Glorification of violence or military action, especially against other groups. 
- **Suppression of Dissent**: Language that delegitimizes critics or opposing viewpoints, and suppresses political opponents. 
- **Anti-Intellectualism**: Disdain for experts, education, or nuanced debate. Appeals to populism over science.

In addition the tool utilizes: 
**Overall Sentiment** Evaluates the emotional tone of the speech to detect extreme positivity or negativity. This can be used to detect elements of anger in a speech.
**Entity Recognition and Contextual Analysis**: Leverages spaCy’s Named Entity Recognition (NER) to identify and evaluate contexts involving nationalities, minorities, and political entities.
**Visualization**: Results include radar charts and highlighted sentences categorized by their relevance to fascist traits.

## Overall Metholodogy
### Creation of a Dataset
For this project to be completed a dataset of known fascist speeches had to be created. Please see the dataset here: []()

### The Underlying Algorithms (Spacy)

### Determination of Words & Weights

## Contribute to the Project!






