-- 테이블 생성
-- id : 기사 아이
-- title : 기사 제목
-- link : 기사 링크
-- time : 기사 긁어온 시각

CREATE TABLE crawling.`crawlingDB` (
  `id` varchar(100) NOT NULL,
  `title` varchar(100) NOT NULL,
  `link` varchar(300) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

desc crawling.crawlingDB;

