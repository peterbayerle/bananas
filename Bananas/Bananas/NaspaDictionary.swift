//
//  NaspaDictionary.swift
//  Bananas
//
//  Created by Peter Bayerle on 2/22/23.
//

import Foundation
import SQLite

struct Definition: Hashable {
    var text: String
    var abrevPos: String
    
    init(text: String, abrevPos: String) {
        self.text = !text.isEmpty ? text : "No definition provided"
        self.abrevPos = abrevPos
    }
    
    var pos: String {
        switch abrevPos {
        case "n":
            return "noun"
        case "v":
            return "verb"
        case "article":
            return "article"
        case "conj":
            return "conjunction"
        case "adv":
            return "adverb"
        case "adj":
            return "adjective"
        case "interj":
            return "interjection"
        case "pron":
            return "pronoun"
        case "prep":
            return "preposition"
        default:
            return abrevPos
        }
    }
}

struct Word: Hashable {
    var name: String
    var unparsedDefinitions: String
    var inNwl20: Bool
    var inNwl23: Bool
    
    var definitions: [Definition] {
        unparsedDefinitions.components(separatedBy: ";").map {
            let args = $0.components(separatedBy: ":")
            return Definition(text: args[0], abrevPos: args[1])
        }
    }
    
    static func stub(name: String) -> Word {
        return Word(name: name, unparsedDefinitions: "", inNwl20: false, inNwl23: false)
    }
}

class NaspaDictionary {
    var db: Connection
    
    let words = Table("words")
    let nameCol = Expression<String>("word")
    let defCol = Expression<String>("definitions")
    let inNwl20Col = Expression<Bool>("in_nwl_20")
    let inNwl23Col = Expression<Bool>("in_nwl_23")
    
    init() {
        let path = Bundle.main.path(forResource: "banana-dict", ofType: "sqlite")!
        self.db = try! Connection(path, readonly: true)
    }
    
    func searchWord(_ name: String) -> Word {
        if let word = try? db.pluck(words.filter(nameCol == name)) {
            return Word(name: word[nameCol], unparsedDefinitions: word[defCol], inNwl20: word[inNwl20Col], inNwl23: word[inNwl23Col])
        } else {
            return Word.stub(name: name)
        }
    }
    
    func randomTwoLetterWord() -> Word {
        var result: [Word] = []
        for word in try! db.prepare(words.filter(nameCol.length == 2)) {
            result.append(Word(name: word[nameCol], unparsedDefinitions: word[defCol], inNwl20: word[inNwl20Col], inNwl23: word[inNwl23Col]))
        }
        
        return result.randomElement()!
    }
}
