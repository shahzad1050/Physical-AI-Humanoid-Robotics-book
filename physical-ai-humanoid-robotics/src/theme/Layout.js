import React from 'react';
import Layout from '@theme-original/Layout';
import RAGChatbot from '@site/src/components/RAGChatbot';

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props}>
        {props.children}
        <RAGChatbot />
      </Layout>
    </>
  );
}