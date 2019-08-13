from suds.client import Client
import os
import csv


METADATA_WSDL = 'file:///%s/metadata.xml.wsdl' % os.getcwd()
SOAP_WSDL = 'file:///%s/soap.xml.wsdl' % os.getcwd()

USERNAME = 'XXX'
PASSWORD = 'XXX'

class Metadata():
    """
    Holds methods to retrieve metadata
    """

    access_token = None
    metadata_url = None

    def get_metadata_client(self):
        """
        Get the metadata client
        """
        # Init metadata client
        metadata_client = Client(METADATA_WSDL)
        metadata_client.set_options(location=self.metadata_url)

        # Set the Sessoin Header
        session_header = metadata_client.factory.create("SessionHeader")
        session_header.sessionId = self.access_token
        metadata_client.set_options(soapheaders=session_header)

        return metadata_client

    def write_csv(self, csv_data):
        """
        Write CSV data to file
        """

        with open('output.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(csv_data)

    def list_metadata_for_type(self, type_name):
        """
        Get for a specific type
        """

        # Init metadata client
        metadata_client = self.get_metadata_client()

        # Init the component
        component = metadata_client.factory.create("ListMetadataQuery")
        component.type = type_name

        csv_data = []
        
        for component in metadata_client.service.listMetadata([component], 46):
            print(component)
            row = [
                component.manageableState if hasattr(component, 'manageableState') else None,
                component.type,
                component.fullName,
                component.createdByName,
                component.createdDate,
                component.lastModifiedByName,
                component.lastModifiedDate
            ]
            csv_data.append(row)

        self.write_csv(csv_data)


    def list_metadata(self):
        """
        Retrieve metadata from the Org
        """

        # Init metadata client
        metadata_client = self.get_metadata_client()

        print('Listing all metadata...\n')

        component_list = []
        loop_counter = 0

        all_metadata = metadata_client.service.describeMetadata(46)

        csv_data = []

        for component_type in all_metadata[0]:

            if not component_type.inFolder:

                if 'childXmlNames' in component_type:

                    child_component_list = []
                    child_loop_counter = 0

                    for child_component in component_type.childXmlNames:
                        if child_component not in ['AutoResponseRule','MatchingRule','EscalationRule','AssignmentRule']:
                            component = metadata_client.factory.create("ListMetadataQuery")
                            component.type = child_component
                            child_component_list.append(component)
                            if len(child_component_list) >= 3 or (len(component_type.childXmlNames) - child_loop_counter) <= 3:
                                for component in metadata_client.service.listMetadata(component_list, 46):
                                    row = [
                                        component.manageableState if hasattr(component, 'manageableState') else None,
                                        component.type,
                                        component.fullName,
                                        component.createdByName,
                                        component.createdDate,
                                        component.lastModifiedByName,
                                        component.lastModifiedDate
                                    ]
                                    csv_data.append(row)
                                child_component_list = []
                            child_loop_counter = child_loop_counter + 1

                component = metadata_client.factory.create("ListMetadataQuery")
                component.type = component_type.xmlName
                component_list.append(component)

            if len(component_list) >= 3 or (len(all_metadata[0]) - loop_counter) <= 3:
                for component in metadata_client.service.listMetadata(component_list, 46):
                    row = [
                        component.manageableState if hasattr(component, 'manageableState') else None,
                        component.type,
                        component.fullName,
                        component.createdByName,
                        component.createdDate,
                        component.lastModifiedByName,
                        component.lastModifiedDate
                    ]
                    csv_data.append(row)
                component_list = []

            loop_counter = loop_counter + 1

        # Write the data to CSV
        self.write_csv(csv_data)


    def get_access_token(self):
        """
        Login using SOAP API to retrieve access token
        """

        soap_client = Client(SOAP_WSDL)

        print('Logging into Salesforce...\n')
        login_result = soap_client.service.login(USERNAME, PASSWORD)

        # Set access token and metadata url
        self.access_token = login_result.sessionId
        self.metadata_url = login_result.metadataServerUrl

        print('Logged in and session ID retrieved: \n' + self.access_token + '\n')
        print('Metadata URL: ' + self.metadata_url + '\n')

    def __init__(self):
        # Retrieve the access token
        self.get_access_token()



if __name__ == '__main__':
    metadata_service = Metadata()
    metadata_service.list_metadata()
    #metadata_service.list_metadata_for_type('CustomField')
