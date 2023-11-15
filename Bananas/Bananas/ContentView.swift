//
//  ContentView.swift
//  Bananas
//
//  Created by Peter Bayerle on 2/22/23.
//

import SwiftUI
import Combine

struct ContentView: View {
    private var dict: NaspaDictionary
    @State private var searchedWord: Word
    
    init() {
        let dict = NaspaDictionary()
        self.dict = dict
        self.searchedWord = dict.randomTwoLetterWord()
    }
    
    private func updateWord(_ word: String) {
        if (!word.isEmpty) {
            searchedWord = dict.searchWord(word)
        }
    }
    
    var body: some View {
        NavigationStack {
            WordCard(searchedWord)
            .padding(.top, 50)
            .padding(.horizontal, 25)
            Spacer()
            WordSearchBar { updateWord($0) }
            .padding()
        }
    }
}

struct WordCard: View {
//    @State private var showNwl20 = UserDefaults.standard.bool(forKey: "ShowNwl20")
//    @State private var showNwl23 = UserDefaults.standard.bool(forKey: "showNwl23")

    private var word: Word
    
    init(_ word: Word) {
        self.word = word
    }
    
    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                Text(word.name)
                    .font(.largeTitle)
                    .bold()
                    .lineLimit(1)
                    .truncationMode(.tail)
                Spacer()
                if (word.inNwl20 || word.inNwl23) {
                    NavigationLink {
                        DefinitionView(word)
                    } label: {
                        HStack {
                            Text("Define")
                            Image(systemName: "chevron.right")
                        }
                    }
                }
            }
            .padding(.horizontal, 15)
            
            Divider()
            VStack(alignment: .center) {
                HStack {
                    Text("NASPA Word List (2020)")
                    Spacer()
                    Text(word.inNwl20 ? "Yes" : "No")
                        .foregroundColor(word.inNwl20 ? .green : .red)
                        .font(.title3)
                }
                HStack {
                    Text("NASPA Word List (2023)")
                    Spacer()
                    Text(word.inNwl23 ? "Yes" : "No")
                        .foregroundColor(word.inNwl23 ? .green : .red)
                        .font(.title3)
                }
            }
            .padding(.horizontal, 45)
            .padding(.top, 15)
        }
    }
}
    
struct WordSearchBar: View {
    @FocusState private var fieldIsFocused: Bool
    @State private var wordInSearchBox: String = ""
    var callback: (_: String) -> Void

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
            TextField(
                "Search NASPA Word List ...",
                text: $wordInSearchBox
            )
            .autocorrectionDisabled()
            .autocapitalization(.none)
            .submitLabel(.search)
            .keyboardType(.alphabet)
            .textFieldStyle(.roundedBorder)
            .onSubmit {
                callback(wordInSearchBox)
            }
            .focused($fieldIsFocused)
            .onAppear {
                fieldIsFocused = true
            }
            .onReceive(Just(wordInSearchBox)) { newValue in
                let filtered = newValue.lowercased().filter { "abcdefghijklmnopqrstuvwxyz".contains($0) }
                self.wordInSearchBox = filtered
            }
            .showClearButton($wordInSearchBox, $fieldIsFocused)
        }
    }
}

struct DefinitionView: View {
    var word: Word
    
    init(_ word: Word) {
        self.word = word
    }
    
    var body: some View {
        VStack(alignment: .leading) {
            List(word.definitions, id: \.self) { definition in
                VStack(alignment: .leading) {
                    HStack {
                        Text(word.name).bold()
                        Text(" • ").bold()
                        Text(definition.pos).italic()
                    }
                    .padding(.bottom, 2)
                    
                    Text("\(definition.text)")
                }
            }
            Spacer()
            Text("NASPA Word List 2023 Edition © NASPA 2023. The copy included in this app is licensed for personal use. You may not use it for any commercial purposes.")
                .font(.caption)
                .padding(.horizontal, 30)
                .padding(.top, 10)
                .padding(.bottom, 10)
        }
        
    }
}

struct TextFieldClearButton: ViewModifier {
    // https://www.hackingwithswift.com/forums/100-days-of-swift/adding-a-clear-button-to-a-textfield/12079
    @Binding var fieldText: String
    var focused: FocusState<Bool>.Binding

    func body(content: Content) -> some View {
        content
            .overlay {
                if !fieldText.isEmpty {
                    HStack {
                        Spacer()
                        Button {
                            fieldText = ""
                            focused.wrappedValue = true
                        } label: {
                            Image(systemName: "multiply.circle.fill")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 26, height: 26)
                        }
                        .foregroundColor(.secondary)
                        .padding(.trailing, 4)
                    }
                }
            }
    }
}

extension View {
    func showClearButton(_ text: Binding<String>, _ focused: FocusState<Bool>.Binding) -> some View {
            self.modifier(TextFieldClearButton(fieldText: text, focused: focused))
        }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
