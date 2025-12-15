import React from 'react';
import Root from '@theme-original/Root';
import RAGChatbot from '@site/src/components/RAGChatbot';

export default function RootWrapper(props) {
  return (
    <>
      <Root {...props} />
      <RAGChatbot />
    </>
  );
}
