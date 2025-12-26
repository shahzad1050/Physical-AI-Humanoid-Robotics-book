// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'An Online Textbook',
  favicon: 'img/favicon.ico',

  url: 'https://physical-ai-humanoid-book.vercel.app',
  baseUrl: '/',

  organizationName: 'shahzad1050',
  projectName: 'Physical-AI-Humanoid-Robotics-book',

  onBrokenLinks: 'throw',

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: false, // Disable blog for simplification
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Physical AI & Humanoid Robotics',
        logo: {
          alt: 'Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Modules',
          },
        ],
      },
      footer: {}, // Empty footer for simplification
      prism: {
        theme: require('prism-react-renderer/themes/github'),
        darkTheme: require('prism-react-renderer/themes/dracula'),
      },
    }),
};

module.exports = config;