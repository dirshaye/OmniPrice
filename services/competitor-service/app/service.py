import grpc
from app.proto import competitor_service_pb2
from app.proto import competitor_service_pb2_grpc
from app.database import Competitor, CompetitorProduct
from beanie.exceptions import DocumentNotFound

class CompetitorService(competitor_service_pb2_grpc.CompetitorServiceServicer):
    async def CreateCompetitor(self, request, context):
        try:
            competitor = Competitor(
                name=request.name,
                domain=request.domain,
                website_url=request.website_url,
                description=request.description,
                scraping_enabled=request.scraping_enabled,
                scraping_frequency=request.scraping_frequency
            )
            await competitor.insert()
            return competitor_service_pb2.CompetitorResponse(success=True, message="Competitor created successfully", competitor=competitor.dict())
        except Exception as e:
            return competitor_service_pb2.CompetitorResponse(success=False, message=str(e))

    async def GetCompetitor(self, request, context):
        try:
            competitor = await Competitor.get(request.id)
            if not competitor:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Competitor not found")
                return competitor_service_pb2.CompetitorResponse()
            return competitor_service_pb2.CompetitorResponse(success=True, competitor=competitor.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Competitor not found")
            return competitor_service_pb2.CompetitorResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return competitor_service_pb2.CompetitorResponse()

    async def UpdateCompetitor(self, request, context):
        try:
            competitor = await Competitor.get(request.id)
            if not competitor:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Competitor not found")
                return competitor_service_pb2.CompetitorResponse()

            update_data = request.dict(exclude_unset=True)
            await competitor.update({"$set": update_data})
            return competitor_service_pb2.CompetitorResponse(success=True, message="Competitor updated successfully", competitor=competitor.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Competitor not found")
            return competitor_service_pb2.CompetitorResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return competitor_service_pb2.CompetitorResponse()

    async def DeleteCompetitor(self, request, context):
        try:
            competitor = await Competitor.get(request.id)
            if not competitor:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Competitor not found")
                return competitor_service_pb2.DeleteCompetitorResponse()
            await competitor.delete()
            return competitor_service_pb2.DeleteCompetitorResponse(success=True, message="Competitor deleted successfully")
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Competitor not found")
            return competitor_service_pb2.DeleteCompetitorResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return competitor_service_pb2.DeleteCompetitorResponse()

    async def ListCompetitors(self, request, context):
        try:
            competitors = await Competitor.find_all().to_list()
            return competitor_service_pb2.ListCompetitorsResponse(competitors=[c.dict() for c in competitors])
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return competitor_service_pb2.ListCompetitorsResponse()
