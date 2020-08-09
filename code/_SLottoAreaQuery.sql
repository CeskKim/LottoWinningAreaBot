delimiter $$

DROP PROCEDURE IF EXISTS Lotto._SLottoAreaQuery$$

CREATE PROCEDURE Lotto._SLottoAreaQuery
( 
  IN IN_Addr       VARCHAR(1000) CHARSET utf8
)
BEGIN
       
    SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;                    
    SELECT A.StoreName, A.Addr,A.TCnt, A.FCnt, A.SCnt                                 
      FROM(
            SELECT StoreName, Addr, SUM(1) AS TCnt,
                   SUM(CASE WHEN RankNo = 1 THEN 1 ELSE 0 END) AS FCnt,
                   SUM(CASE WHEN RankNo = 2 THEN 1 ELSE 0 END) AS SCnt
              FROM tbllottoarea
             WHERE Addr LIKE CONCAT('%', IN_Addr, '%')
            GROUP BY StoreName, Addr) AS A
    ORDER BY A.TCnt DESC
    LIMIT 5;
      
END$$
delimiter;




