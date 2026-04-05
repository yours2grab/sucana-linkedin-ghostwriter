-- Ghostwriter Skill — Supabase Setup
-- Run this once in the Supabase SQL Editor
-- Creates pgvector extension and 3 tables for semantic search

-- Enable pgvector extension
create extension if not exists vector;

-- Knowledge chunks: embedded doc fragments for context injection
create table if not exists knowledge_chunks (
  id bigint generated always as identity primary key,
  content text not null,
  source_file text not null,
  chunk_index int not null default 0,
  token_count int,
  embedding vector(1536),
  created_at timestamptz default now()
);

-- Swipe embeddings: saved inspiration posts for style reference
create table if not exists swipe_embeddings (
  id bigint generated always as identity primary key,
  content text not null,
  author text,
  tags text[] default '{}',
  embedding vector(1536),
  created_at timestamptz default now()
);

-- Template embeddings: hooks and frameworks for suggestion
create table if not exists template_embeddings (
  id bigint generated always as identity primary key,
  type text not null check (type in ('hook', 'framework')),
  name text not null,
  structure jsonb,
  category text,
  embedding vector(1536),
  created_at timestamptz default now()
);

-- Similarity search function (convenience wrapper)
create or replace function match_vectors(
  query_embedding vector(1536),
  target_table text,
  match_count int default 5
)
returns table (
  id bigint,
  content text,
  similarity float
)
language plpgsql
as $$
begin
  if target_table = 'knowledge_chunks' then
    return query
      select k.id, k.content, 1 - (k.embedding <=> query_embedding) as similarity
      from knowledge_chunks k
      where k.embedding is not null
      order by k.embedding <=> query_embedding
      limit match_count;
  elsif target_table = 'swipe_embeddings' then
    return query
      select s.id, s.content, 1 - (s.embedding <=> query_embedding) as similarity
      from swipe_embeddings s
      where s.embedding is not null
      order by s.embedding <=> query_embedding
      limit match_count;
  elsif target_table = 'template_embeddings' then
    return query
      select t.id, t.name::text as content, 1 - (t.embedding <=> query_embedding) as similarity
      from template_embeddings t
      where t.embedding is not null
      order by t.embedding <=> query_embedding
      limit match_count;
  end if;
end;
$$;
