
delimiter $$

DROP PROCEDURE IF EXISTS Lotto._SLottoAreaSave$$

CREATE PROCEDURE Lotto._SLottoAreaSave
(
  IN WinNo      INT           ,
  IN RankNo     INT           ,
  IN Serl       INT           ,
  IN StoreName  VARCHAR(255)  ,
  IN Addr       VARCHAR(1000)  
  
)
BEGIN
    DECLARE ERR INT DEFAULT 0;
    DECLARE continue handler for SQLEXCEPTION SET ERR = -1;       
    
    INSERT INTO tbllottoarea
    SELECT WinNo, RankNo, Serl, StoreName, Addr
      FROM dual 
     WHERE NOT EXISTS(SELECT 1
                        FROM tbllottoarea AS A 
                       WHERE WinNo  = A.WinNo
                         AND RankNo = A.RankNo
                         AND Serl   = A.Serl);
       
    
    IF ERR < 0 THEN
       ROLLBACK;
    ELSE
       COMMIT;
     
    END IF;
    
    
    
     
END$$
delimiter;




