package main

import (
	"database/sql"
	"testing"

	waProto "go.mau.fi/whatsmeow/binary/proto"
	waCommon "go.mau.fi/whatsmeow/proto/waCommon"
	"google.golang.org/protobuf/proto"
)

func TestExtractTextContentCaptions(t *testing.T) {
	cases := map[string]*waProto.Message{
		"text":    {Conversation: proto.String("text")},
		"image":   {ImageMessage: &waProto.ImageMessage{Caption: proto.String("image")}},
		"video":   {VideoMessage: &waProto.VideoMessage{Caption: proto.String("video")}},
		"wrapped": {DocumentWithCaptionMessage: &waProto.FutureProofMessage{Message: &waProto.Message{DocumentMessage: &waProto.DocumentMessage{Caption: proto.String("wrapped"), FileName: proto.String("a.pdf")}}}},
	}
	for want, msg := range cases {
		if got := extractTextContent(msg); got != want {
			t.Errorf("extractTextContent(%s) = %q", want, got)
		}
	}
	fwd := &waProto.ContextInfo{IsForwarded: proto.Bool(true)}
	for name, msg := range map[string]*waProto.Message{
		"text":    {ExtendedTextMessage: &waProto.ExtendedTextMessage{Text: proto.String("t"), ContextInfo: fwd}},
		"image":   {ImageMessage: &waProto.ImageMessage{ContextInfo: fwd}},
		"wrapped": {DocumentWithCaptionMessage: &waProto.FutureProofMessage{Message: &waProto.Message{DocumentMessage: &waProto.DocumentMessage{ContextInfo: fwd}}}},
	} {
		if !isForwarded(msg) {
			t.Errorf("isForwarded(%s) = false", name)
		}
	}
	if isForwarded(cases["text"]) || isForwarded(cases["image"]) {
		t.Error("isForwarded on a message without the label = true")
	}
	wrapped := cases["wrapped"]
	if mediaType, filename, _, _, _, _, _ := extractMediaInfo(wrapped); mediaType != "document" || filename != "a.pdf" {
		t.Errorf("extractMediaInfo(wrapped) = %q, %q", mediaType, filename)
	}
}

func TestApplyProtocolMessage(t *testing.T) {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	db.Exec("CREATE TABLE messages (id TEXT, chat_jid TEXT, content TEXT)")
	db.Exec("INSERT INTO messages VALUES ('a', 'c', 'old'), ('b', 'c', 'gone'), ('a', 'other', 'keep')")
	store := &MessageStore{db: db}
	key := func(id string) *waCommon.MessageKey { return &waCommon.MessageKey{ID: proto.String(id)} }

	// Shapes as whatsmeow delivers them: an edited caption, an empty edit (ignored), a revoke
	for _, pm := range []*waProto.ProtocolMessage{
		{Type: waProto.ProtocolMessage_MESSAGE_EDIT.Enum(), Key: key("a"), EditedMessage: &waProto.Message{ImageMessage: &waProto.ImageMessage{Caption: proto.String("new")}}},
		{Type: waProto.ProtocolMessage_MESSAGE_EDIT.Enum(), Key: key("a"), EditedMessage: &waProto.Message{}},
		{Type: waProto.ProtocolMessage_REVOKE.Enum(), Key: key("b")},
	} {
		if err := applyProtocolMessage(store, "c", pm); err != nil {
			t.Fatal(err)
		}
	}
	got := map[string]string{}
	rows, _ := db.Query("SELECT id || '/' || chat_jid, content FROM messages")
	for rows.Next() {
		var k, v string
		rows.Scan(&k, &v)
		got[k] = v
	}
	if len(got) != 2 || got["a/c"] != "new" || got["a/other"] != "keep" {
		t.Errorf("rows after edit + revoke = %v", got)
	}
}
