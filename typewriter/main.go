package main

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/charmbracelet/bubbles/textarea"
	tea "github.com/charmbracelet/bubbletea"
)

type model struct {
	text textarea.Model
	url  string
	err  error
}

type TextBody struct {
	Text string `json:"text"`
}

func initModel(url string) model {
	text := textarea.New()
	text.SetWidth(70)
	text.SetHeight(20)
	text.Placeholder = "Let's get you printed ... "
	text.Focus()
	return model{
		text: text,
		url:  url,
		err:  nil,
	}
}

func (m model) Init() tea.Cmd {
	return textarea.Blink
}

func (m model) View() string {
	var text string
	text += "running on url" + m.url + "\t = \t" + "http://" + m.url + "/print_text" + "\n"
	text += "Hello, Typewriter!\nprint something awesome...\n(press escape to exit and print)\n"
	text += m.text.View() + "\n"
	return text
}

func (m model) Update(message tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd
	var cmd tea.Cmd
	switch msg := message.(type) {
	case tea.KeyMsg:
		switch msg.Type {
		case tea.KeyEsc:
			if m.text.Value() != "" {
				textbody := TextBody{Text: m.text.Value()}
				jsonbody, err := json.Marshal(textbody)
				if err != nil {
					m.err = err
					log.Fatal(err)
					return m, tea.Quit
				}

				resp, err := http.Post("http://"+m.url+"/print_text", "application/json", bytes.NewBuffer(jsonbody))
				if err != nil {
					m.err = err
					log.Fatal(err)
					return m, tea.Quit
				}
				defer resp.Body.Close()
			}
			return m, tea.Quit
		}
	}
	m.text, cmd = m.text.Update(message)
	cmds = append(cmds, cmd)
	return m, tea.Batch(cmds...)
}

func main() {
	url := os.Args[1]
	p := tea.NewProgram(initModel(url))
	if _, err := p.Run(); err != nil {
		log.Fatal(err)
	}
}
