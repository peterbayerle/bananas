//
//  ContentView.swift
//  Bananas
//
//  Created by Peter Bayerle on 2/22/23.
//

import SwiftUI
import Combine

struct ContentView: View {
    @State private var searchedWord: String = "ka"

    var body: some View {
        NavigationStack {
            WordCard(searchedWord)
            .padding(.top, 50)
            .padding(.horizontal, 25)
            Spacer()
            WordSearchBar {
                (wordInSearchBox: String) -> ()  in
                searchedWord = wordInSearchBox
            }
            .padding()
        }
    }
}

struct WordCard: View {
    private var dict = NaspaDictionary()

    var word: String
    
    private var isInDict: Bool {
        dict.check(word)
    }
    
    init(_ word: String) {
        self.word = word
    }
    
    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                Text(word)
                    .font(.largeTitle)
                    .bold()
                    .lineLimit(1)
                    .truncationMode(.tail)
                Spacer()
                if (isInDict) {
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
            HStack(alignment: .center) {
                Text("NASPA Word List (2020)")
                Spacer()
                Text(isInDict ? "Yes" : "No")
                    .foregroundColor(isInDict ? .green : .red)
                    .font(.title3)
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
                "Search NASPA dictionary ...",
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
    var word: String
    private var dict = NaspaDictionary()
    
    init(_ word: String) {
        self.word = word
    }
    
    var body: some View {
        VStack(alignment: .leading) {
            List(dict.fetchDefinitions(word), id: \.self) { word in
                VStack(alignment: .leading) {
                    HStack {
                        Text(word.word).bold()
                        Text(" • ").bold()
                        Text(word.pos).italic()
                    }
                    .padding(.bottom, 2)
                    
                    Text("\(word.definition)")
                }
            }
            Spacer()
            Text("NASPA Word List 2020 Edition © NASPA 2020. The copy included in this app is licensed for personal use. You may not use it for any commercial purposes.")
                .font(.caption)
                .padding(.horizontal, 30)
                .padding(.top, 10)
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
