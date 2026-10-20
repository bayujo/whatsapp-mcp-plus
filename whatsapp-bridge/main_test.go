package main

import (
	"testing"

	waProto "go.mau.fi/whatsmeow/binary/proto"
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
	wrapped := cases["wrapped"]
	if mediaType, filename, _, _, _, _, _ := extractMediaInfo(wrapped); mediaType != "document" || filename != "a.pdf" {
		t.Errorf("extractMediaInfo(wrapped) = %q, %q", mediaType, filename)
	}
}
