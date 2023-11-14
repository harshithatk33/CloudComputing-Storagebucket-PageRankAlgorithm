import apache_beam as beam
import re
import argparse
import os 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./googleCredentials.json"

from apache_beam.options.pipeline_options import PipelineOptions

class CustomHTMLProcessor(beam.DoFn):
    def process(self, input_element):
        file_name, content = input_element
        import re
        pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="(\d+\.html)"', re.IGNORECASE)
        found_matches = pattern.findall(content)
        match_list = []
        for link in found_matches:
            match_list.append((file_name, link))
        
        return match_list

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--runner", help="Pipeline Runner", type=str, default="DataflowRunner")
    parser.add_argument("-p", "--project", help="GCP Project", type=str, default="quiet-sanctuary-399018")
    parser.add_argument("-t", "--temp_location", help="Temp Location", type=str, default="gs://cds-561-assignemnt7-bucket/temp")
    parser.add_argument("-i", "--input", help="Input Bucket Path", type=str, default='gs://cds561-assignment2-harshitha/fileGeneration')
    parser.add_argument("-rg", "--region", help="Region", type=str, default="us-east4")
    parser.add_argument("-o", "--output", help="Output Bucket Path", type=str, default="gs://cds-561-assignemnt7-bucket/output")
    args = parser.parse_args()

    poptions = PipelineOptions(runner=f'{args.runner}',
                                       project=f'{args.project}',
                                       temp_location=f'{args.temp_location}',
                                       region=f'{args.region}')
   
    with beam.Pipeline(options=poptions) as p_line:
        file_data = (p_line | 'read_files' >> beam.io.ReadFromTextWithFilename(f'{args.input}/*.html') \
                | 'get_links' >> beam.ParDo(CustomHTMLProcessor()))
        
        out_count = (file_data | 'count_Outgoing' >> beam.combiners.Count.PerKey() \
                                | 'out_top_five_results' >> beam.transforms.combiners.Top.Of(5, key=lambda x: x[1]) \
                                | 'out_write_to_SB' >> beam.io.WriteToText(f'{args.output}/out'))

        in_count = (file_data | 'in_custom_transform' >> beam.Map(lambda link: (link[1], link[0]))
                            | 'count_incoming' >> beam.combiners.Count.PerKey() \
                            | 'in_top_five_results' >> beam.transforms.combiners.Top.Of(5, key=lambda x: x[1]) \
                            | 'tn_write_to_SB' >> beam.io.WriteToText(f'{args.output}/in'))
    

if __name__ == '__main__':
    main()