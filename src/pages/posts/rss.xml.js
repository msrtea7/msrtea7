import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // 获取所有分类的文章
  const [academic, alcohol, daily, martial, sound] = await Promise.all([
    getCollection('academic'),
    getCollection('alcohol'),
    getCollection('daily'),
    getCollection('martial'),
    getCollection('sound')
  ]);

  // 合并所有文章
  const allPosts = [...academic, ...alcohol, ...daily, ...martial, ...sound];

  // 按发布时间倒序排列
  allPosts.sort((a, b) => new Date(b.data.pubDate) - new Date(a.data.pubDate));

  return rss({
    title: '你的网站标题',
    description: '你的网站描述',
    site: context.site,
    items: allPosts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      // 根据你的路由结构生成链接
      link: `/posts/${post.id}/`,
      // 未来如果添加了 description 字段，会自动包含
      ...(post.data.description && { description: post.data.description }),
    })),
  });
}