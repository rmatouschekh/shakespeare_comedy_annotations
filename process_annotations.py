import os
import re
import sys
import json

def sort_keys(dict):
    # Sort the keys of a dictionary by value
    reverse_dict = {v: k for k, v in dict.items()}

    sorted_values = list(reverse_dict.keys())
    sorted_values.sort(reverse=True)
    sorted_values = [reverse_dict[item] for item in sorted_values if reverse_dict[item] != "Total"]

    return sorted_values


def rank_keys(dict):
    # Return a new dictionary with key rank : old key pairs
    sorted_values = sort_keys(dict)
    sorted_names = {}

    for i, value in enumerate(sorted_values):
        sorted_names[i+1] = value

    return sorted_names


def sort_dict(dict):
    # Return a new dictionary with old key : key rank pairs
    sorted_values = sort_keys(dict)
    sorted_names = {}

    for i, value in enumerate(sorted_values):
        sorted_names[value] = i+1
    
    return sorted_names


def mark_highest(play, sorted_dict, results):
    # Mark the highest ranked character
    for entry in results:
        if entry["Play"] == play and entry["Speaker"] == sorted_dict[1]:
            entry["Highest"] = "Yes"


def update_play_stats(play_statistics, sorted_plays, key):
    # Add rank to play statistics
    for entry in play_statistics:
        rank = sorted_plays[entry["Play"]]
        entry[key] = rank


def convert_to_scene(act, scene):
    # Convert the act and scene to roman numerals to match chart labels
    acts = ["INDUCTION", "ACT 1", "ACT 2", "ACT 3", "ACT 4", "ACT 5", "EPILOGUE"]
    convert_to_roman = {0: "Induction", 1: "i", 2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi", 7: "vii", 8: "viii", 9: "ix"}
    sc = convert_to_roman[scene]

    if acts.index(act) not in [0, 6]:
        act_rep = convert_to_roman[acts.index(act)].upper() + "." + sc
    else:
        act_rep = act.capitalize()
        if acts.index(act) == 0:
            act_rep += "." + sc
    
    return act_rep


def scene_not_empty(scene):
    # Find whether scene exists in play
    total = 0
    for name in scene:
        total += scene[name]
    if total > 0:
        return True
    return False


def make_name_dict(names):
    # Make a dictionary with each name as a key set each value to 0
    scene = {}
    for name in names:
        scene[name] = 0
    scene["Total"] = 0
    return scene


def make_name_list_dict(names):
    # Make a dictionary with each name as a key and set each value to an empty list
    scene = {}
    for name in names:
        scene[name] = []
    scene["Total"] = []
    return scene


def find_full_name(char, names, play):
    # Find the full name of a character
    if "Much" in play and char == "PRINCE":
        return "DON PEDRO"
    
    part_name = ""
    for name in names:
        if char == name:
            return name
        elif char in name:
            part_name = name
    
    return part_name


def find_speaker(words):
    # Given a line of speech return speakers  
    words = words.split()
    speaker_break = 0

    # Find the break between speaker names and speech
    for word in words:
        if word.isupper() and len(re.sub(r'[^\w\s]', '', word)) > 1 and (len(word) - len(re.sub(r'[^\w\s/]', '', word))) <= 1:
            speaker_break += 1
        else:
            break
    
    # Clean speaker names and return as list
    speaker = words[:speaker_break]
    speaker = [word.replace(",", "") for word in speaker]
    speaker = " ".join(speaker)
    rest = " ".join(words[speaker_break:])

    return speaker.split("/"), rest


def process_words(words):
    # Remove any text in square brackets
    starts = [s.start() for s in re.finditer('\[', words)]
    ends = [e.start() for e in re.finditer('\]', words)]
    if len(starts) != len(ends):
        print("Different number of start and end brackets")
        sys.exit()
    else:
        for i in range(len(starts)-1, -1, -1):
            if ends[i]+1 == len(words):
                words = words[:starts[i]]
            else:
                words = words[:starts[i]] + words[ends[i]+1:]
    return len(words.split())


def calculate_a_percentage(num_words, total):
    # Calculate what proportion of total num_words is
    return (num_words/total)*100


def calculate_percentages(play, female_characters, total_words, total_impact):
    # Transform counts to percentages and remove non-female characters
    global results, weighted_results, self_results

    # Transform each count to a percentage
    # Identify non-female character information
    to_delete = []
    for act in results[play]:
        for i in range(len(results[play][act])):
            for char in results[play][act][i]:
                if char in female_characters or char == "Total":
                    results[play][act][i][char] = calculate_a_percentage(results[play][act][i][char], total_words)
                    weighted_results[play][act][i][char] = calculate_a_percentage(weighted_results[play][act][i][char], total_impact)
                    self_results[play][act][i][char] = calculate_a_percentage(self_results[play][act][i][char], total_words)
                elif char != "Total":
                    to_delete.append([act, i, char])
    
    # Delete non-female character information
    for item in to_delete:
        scene = results[play][item[0]][item[1]]
        scene.pop(item[2])
        weight_scene = weighted_results[play][item[0]][item[1]]
        weight_scene.pop(item[2])
        self_scene = self_results[play][item[0]][item[1]]
        self_scene.pop(item[2])


def update_results_dict(char, result, results_dict):
    # Update results for a character in a results dict with new scene data
    if char not in results_dict:
        results_dict[char] = result
    else:
        results_dict[char] += result
    
    return results_dict


def create_entry_dict(play, char, scene, info, num_chars):
    # Create info dict for a given play, char, scene, and mode combo
    entry_dict = {"Play": play, "Speaker": char, "Scene": scene, "Percentage": info, "Highest": "No"}
    if num_chars > -1:
        entry_dict["NumCharacters"] = num_chars
    return entry_dict


def reformat_play(play, processed_results, processed_weighted_results, processed_self_results, play_statistics):
    # Calculate summary statistics for and process a given play
    global results, weighted_results, num_characters

    weighted_results_dict = {}
    results_dict = {}
    sum = 0
    weighted_sum = 0

    for act in results[play]:
        for s in range(len(results[play][act])):
            scene = convert_to_scene(act, s+1)
            for char in results[play][act][s]:
                results_dict = update_results_dict(char, results[play][act][s][char], results_dict)
                weighted_results_dict = update_results_dict(char, weighted_results[play][act][s][char], weighted_results_dict)

                if char != "Total":
                    sum += results[play][act][s][char]
                    weighted_sum += weighted_results[play][act][s][char]
                
                processed_results.append(create_entry_dict(play, char, scene, results[play][act][s][char], -1))
                processed_weighted_results.append(create_entry_dict(play, char, scene, weighted_results[play][act][s][char], len(list(set(num_characters[play][act][s][char])))))
                processed_self_results.append(create_entry_dict(play, char, scene, self_results[play][act][s][char], -1))
    
    w_sorted_names = rank_keys(weighted_results_dict)
    sorted_names = rank_keys(results_dict)
    for item in [processed_results, processed_weighted_results, processed_self_results]:
        mark_highest(play, w_sorted_names, item)
    play_statistics.append({"Play": play, "WeightedCharRanks": w_sorted_names, "CharRanks": sorted_names, "WeightedCharRankValues": weighted_results_dict, "CharRankValues": results_dict})

    return sum, weighted_sum


def reformat_results():
    # Calculate summary statistics for and process each play, general statistics
    global results

    processed_results = []
    processed_weighted_results = []
    processed_self_results = []
    play_statistics = []
    play_ranks = {}
    weighted_play_ranks = {}

    for play in results:
        sum, weighted_sum = reformat_play(play, processed_results, processed_weighted_results, processed_self_results, play_statistics)        
        play_ranks[play] = sum
        weighted_play_ranks[play] = weighted_sum
    
    # Rank each play by percent of total impact spoken by women and percent of total words spoken by women
    sorted_play_ranks = sort_dict(play_ranks)
    sorted_weighted_play_ranks = sort_dict(weighted_play_ranks)

    # Add rank values and totals to play statistics
    rank_dicts = [play_ranks, weighted_play_ranks, sorted_play_ranks, sorted_weighted_play_ranks]
    variable_names = ["RankValue", "WeightedRankValue", "Rank", "WeightedRank"]
    for i in range(4):
        update_play_stats(play_statistics, rank_dicts[i], variable_names[i])

    return processed_results, processed_weighted_results, processed_self_results, play_statistics


def initialize_play_dictionaries(play):
    # Add play as key to each result dictionary with blank dictionary value
    results[play] = {}
    weighted_results[play] = {}
    num_characters[play] = {}
    self_results[play] = {}


def reset_acts():
    # Reset all acts back to empty lists
    act = []
    weighted_act = []
    num_characters_act = []
    self_act = []
    return act, weighted_act, num_characters_act, self_act


def reset_scenes(names):
    # Reset all scenes to empty dictionaries
    scene = make_name_dict(names)
    weighted_scene = make_name_dict(names)
    num_characters_scene = make_name_list_dict(names)
    self_scene = make_name_dict(names)
    return scene, weighted_scene, num_characters_scene, self_scene


def add_acts(play, last_act, act, weighted_act, num_characters_act, self_act):
    # Add new acts to result dictionaries
    results[play][last_act] = act
    weighted_results[play][last_act] = weighted_act
    num_characters[play][last_act] = num_characters_act
    self_results[play][last_act] = self_act


def add_scenes(act, weighted_act, num_characters_act, self_act, scene, weighted_scene, num_characters_scene, self_scene):
    # Add completed scene dictionaries to act lists
    act.append(scene)
    weighted_act.append(weighted_scene)
    num_characters_act.append(num_characters_scene)
    self_act.append(self_scene)


def find_character(line, names, female_characters):
    # Find the name in the line if one exists
    if "ACT" not in line and "INDUCTION" not in line and "SCENE" not in line and "Epilogue" not in line and "EPILOGUE" not in line:
        line = line.strip().split()
        name = ""
        for word in line:
            word = word.replace(",", "")
            if word.isupper():
                name += word + " "
            elif name:
                break
        name = name.strip()
        if len(name) > 1:
            if "*" in name:
                female_characters.append(name.replace("*", ""))
            names.append(name.replace("*", ""))


def no_speaker(spoken_to):
    # Return true if speach is to audience or an exclamation
    return ("Self/Exclamation" in spoken_to)


def update_totals(total_words, total_impact, num_words, spoken_to):
    # Update word and impact totals
    total_words += num_words
    if not no_speaker(spoken_to):
        total_impact += num_words*len(spoken_to)
    return total_words, total_impact


def update_scene_totals(num_words, spoken_to, scene, num_characters_scene, weighted_scene):
    # Update scene totals
    scene["Total"] += num_words
    num_characters_scene["Total"] += spoken_to
    if not no_speaker(spoken_to):
        weighted_scene["Total"] += num_words*len(spoken_to)


def update_scene_speakers(num_words, spoken_to, current_speaker, scene, num_characters_scene, weighted_scene, self_scene):
    # Update speaker totals for scene
    for speaker in current_speaker:
        scene[speaker] += num_words
        weighted_scene[speaker] += num_words*len(spoken_to)
        num_characters_scene[speaker] += spoken_to
        if no_speaker(spoken_to):
            self_scene[speaker] += num_words


def process_speech_line(line, speaker_words, names, play, current_speaker):
    # Add line to speaker words
    if len(re.sub(r'[^\w\s]', '', line.split()[0])) > 1 and line.split()[0].isupper():
        # Find speaker if in line
        line = line.replace("--", " ").strip()
        current_speaker, line = find_speaker(line)

        for i in range(len(current_speaker)):
            current_speaker[i] = find_full_name(current_speaker[i], names, play)
        speaker_words = line + " "
    else:
        line = line.replace("--", " ").strip()
        speaker_words += line + " "
    
    return current_speaker, speaker_words


def process_file(file):
    lines = file.readlines()

    # Play variables
    add_characters = False
    names = []
    female_characters = []
    play = ""
    total_words = 0
    total_impact = 0

    # Act lists
    act = []
    weighted_act = []
    num_characters_act = []
    self_act = []

    # Scene dictionaries
    scene = {}
    weighted_scene = {}
    num_characters_scene = {}
    self_scene = {}

    current_speaker = []
    speaker_words = ""
    last_act = ""
    for index, line in enumerate(lines):
        # Find play name
        if index == 0:
            play = line.strip()
            initialize_play_dictionaries(play)
        
        # Find start of character list
        elif ("=" in line) and ("Characters" in lines[index-1]):
            add_characters = True
        
        # Find character name
        elif add_characters and "=" not in line:
            find_character(line, names, female_characters)
        
        elif "=" in line:
            # No longer adding characters
            if add_characters:
                add_characters = False
            
            # At the start of a new act, add scenes to acts and acts to results, and reset act and scene variables
            if "ACT" in lines[index-1] or "EPILOGUE" in lines[index-1] or "Epilogue" in lines[index-1] or "INDUCTION" in lines[index-1]:
                if last_act:
                    add_scenes(act, weighted_act, num_characters_act, self_act, scene, weighted_scene, num_characters_scene, self_scene)
                    add_acts(play, last_act, act, weighted_act, num_characters_act, self_act)
                
                last_act = re.sub(r'[^\w\s]', '', lines[index-1].strip())
                scene, weighted_scene, num_characters_scene, self_scene = reset_scenes(names)
                act, weighted_act, num_characters_act, self_act = reset_acts()
            
            # At the start of a new scene, add to acts and reset scene variables
            elif "Scene" in lines[index-1]:
                if scene_not_empty(scene):
                    add_scenes(act, weighted_act, num_characters_act, self_act, scene, weighted_scene, num_characters_scene, self_scene)
                scene, weighted_scene, num_characters_scene, self_scene = reset_scenes(names)
        
        # Having found who it is spoken to, process a chunk of speech
        elif "*" in line:
            spoken_to = line.strip().replace("*", "").split(", ")
            num_words = process_words(speaker_words)
            total_words, total_impact = update_totals(total_words, total_impact, num_words, spoken_to)
            update_scene_totals(num_words, spoken_to, scene, num_characters_scene, weighted_scene)
            update_scene_speakers(num_words, spoken_to, current_speaker, scene, num_characters_scene, weighted_scene, self_scene)
            speaker_words = ""
        
        # Add speech line and find new speaker(s)
        elif line.split() and "ACT" not in line and "INDUCTION" not in line and "Scene" not in line and "Epilogue" not in line and "EPILOGUE" not in line:
            current_speaker, speaker_words = process_speech_line(line, speaker_words, names, play, current_speaker)
    
    add_scenes(act, weighted_act, num_characters_act, self_act, scene, weighted_scene, num_characters_scene, self_scene)
    add_acts(play, last_act, act, weighted_act, num_characters_act, self_act)

    calculate_percentages(play, female_characters, total_words, total_impact)


def create_json_file(file_name, results_file):
    # Create a json file of results
    output_file = open("Results/" + file_name + ".json", "w")
    json.dump(results_file, output_file)
    output_file.close()


if __name__ == "__main__":
    results = {}
    weighted_results = {}
    num_characters = {}
    self_results = {}

    # Process each text file in the 'Annotations' folder
    for file in os.listdir("Annotations/"):
        if file.endswith(".txt"):
            print(file)
            open_file = open("Annotations/" + file)
            process_file(open_file)
    
    processed_results, processed_weighted_results, processed_self_results, play_statistics = reformat_results()

    # Output information as JSON files
    create_json_file("weighted_results", processed_weighted_results)
    create_json_file("results", processed_results)
    create_json_file("self_results", processed_self_results)
    create_json_file("play_statistics", play_statistics)