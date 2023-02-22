//
//  NaspaDictionary.swift
//  Bananas
//
//  Created by Peter Bayerle on 2/22/23.
//

import Foundation
import SQLite

struct Word: Hashable {
    var word: String
    var definition: String
    var pos: String
}

class NaspaDictionary {
    var db: Connection
    
    init() {
        let path = Bundle.main.path(forResource: "banana-dict", ofType: "sqlite")!
        self.db = try! Connection(path, readonly: true)
    }
    
    func check(_ name: String) -> Bool {
        let words = Table("words")
        let nameCol = Expression<String>("word_friendly")

        let count = try! db.scalar(words.filter(nameCol == name).count)
        
        return count > 0
    }
    
    
    
    func fetchDefinitions(_ name: String) -> [Word] {
        let words = Table("words")
        let nameCol = Expression<String>("word_friendly")
        let defCol = Expression<String>("definition_friendly")
        let posCol = Expression<String>("pos_friendly")
        
        var result: [Word] = []
        for word in try! db.prepare(words.filter(nameCol == name)) {
            result.append(Word(word: word[nameCol], definition: word[defCol], pos: word[posCol]))
        }
        
        return result
    }
    
}
