# Annotating Who Talks to Whom in Shakespeare's Comedies
*Created by: Rebecca Hicke*  
*Last Updated: 01/06/2023*

This dataset contains all of Shakespeare's comedies annotated for who talks to whom and a processor which analyzes the data. Although the processor is currently designed to output information on female character's speaking roles it can be adapted for other purposes. The visualizations created with this data are [available here](https://observablehq.com/@rhicke/let-every-word-weigh-heavy-of-her-worth).

### Annotations
I used the text file versions of the comedies available online from the Folger Shakespeare Library as the copy texts for these annotations. I have revised the annotations for each play using supplementary information from the Arden Shakespeare Third Series editions and adjusted to the Arden version of the text at several points in these plays.

Under each section of speech there is an asterisk followed by a list of the characters to whom to section is addressed, separated by commas. When there are mutliple speakers, the speaker names are separated by forward slashes, with no spaces in between them. When a section of speech is an exclamation not directed at another character on stage, an aside, or a soliloquy, it is labeled as Self/Exclamation. If a character is addressing someone who is offstage or asleep, and is therefore not able to hear them speak, the section of speech is also labeled Self/Exclamation. When there are any number of unnamed characters on stage who are being addressed, they are grouped together as one and labeled as Other. The annotations only take into account who a section of speech is directed at; if a character hears something spoken, but is not the intended recipient, they are not included in the addresees.

### Code

This code reads annotations from the **Annotations** folder and outputs four json files into the **Results** folder. The code relies on the specific format of the text files from the Folger Shakespeare Library, but should be able to read annotations from any text file of the same format. As it is currently set up, the code outputs four files:

* **results.json:** This file is a list of objects, where each object has the name of a play, a speaker, a scene, the percent of total works spoken by that speaker in that scene, and whether this speaker is the most impactful of the play.
* **weighted_results.json:** This file is nearly identical to **results.json**, but instead of the percentage of total words spoken each object has the percentage of total impact contributed by a speaker in a scene and each object also contains the number of characters a speaker addresses in a scene.
* **self_results.json:** This file is also nearly identical to **results.json**, but instead of the percentage of total words spoken by a speaker, each object contains the percentage of total words in the play a speaker gives as an aside, soliloquy, or exclamation in the scene.
* **play_statistics.json:** This file is a list of objects, with one object for each play. Each object contains the name of the play, a list of characters ranked by the percentage of total impact they contribute, a list of characters ranked by the percentage of total words they speak, a list of characters with the percentage of total impact they contribute, a list of characters with the percentage of total words they speak, the play ranked by what percentage of total impact all female characters contribute, the play ranked by what percentage of total words all female characters speak, and more.

This code is commented, and should be easily adapted if you wish to use it for a different purpose.

**This resource is open for use, but please cite it if you do use it!**
