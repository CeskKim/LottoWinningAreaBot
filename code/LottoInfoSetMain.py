import json
import LottoInfoSet as LIS

def lambda_handler(event, context):
    # TODO implement
    LIS.LottoDbSave()
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
